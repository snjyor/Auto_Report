import json
import os.path
import sys
import time
from pathlib import Path
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts
import openai

ABS_PATH = Path(__file__).parent.absolute()
sys.path.append(str(ABS_PATH))
from configs import configs as cfg
from prompts import Prompts
from utils import utils
from analyse.ai_analyse import AIAnalyse
from analyse.stats_data import get_stats_data


class AiDataAnalysisFrontend(AIAnalyse):
    def __init__(self):
        super().__init__()
        st.set_page_config(page_title="Auto Data Analysis", page_icon="📊", layout="wide")
        st.sidebar.title("AI Data Analysis")

        self.azure_ai = st.sidebar.checkbox("AzureOpenAI", value=False, key="azure_ai")
        self.azure_api_key = st.sidebar.text_input("Azure Api Key", value="")
        self.azure_endpoint = st.sidebar.text_input("Azure Endpoint", value="")
        self.azure_version = st.sidebar.text_input("Azure Version", value="")

        self.openai_api_key = st.sidebar.checkbox("OpenAI Api Key", value=True, key="openai_api_key")
        self.openai_api_key_text = st.sidebar.text_input("OpenAI Api Key", value="")
        st.markdown('<h1 style="text-align: center;">AI Data Analysis</h1>', unsafe_allow_html=True)

    def report_demo(self):
        st.markdown('---', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center;">Example of AI analysis</h3>', unsafe_allow_html=True)
        with st.spinner("正在根据您的数据生成数据分析建议……"):
            time.sleep(0.5)
            with open(os.path.join(ABS_PATH, "analyse", "report_demo.json"), "r") as f:
                reports = json.loads(f.read())
            all_charts_path = []
            for root, path, names in os.walk(os.path.join(ABS_PATH, "export")):
                for name in names:
                    charts_path = os.path.join(root, name)
                    all_charts_path.append(charts_path)
            time.sleep(0.5)
        for report in reports:
            with st.spinner(f"正在根据建议：`{report.get('suggestion')}`生成数据分析图表……"):
                charts_path = [path for path in all_charts_path if report.get("title") in path]
                charts_path = charts_path[0] if charts_path else ""
                with open(charts_path, "r") as f:
                    charts = json.loads(f.read())
                time.sleep(0.5)
                st_echarts(options=charts, height="600px", width="100%")

            with st.spinner(f"正在根据数据图表总结描述信息……"):
                time.sleep(0.5)
                st.write(f"{report.get('description')}")
            st.success(f"`{report.get('suggestion')}` 分析完成")
        st.success("数据分析完成")

    def report(self):
        col1, col2, col3, col4 = st.columns([7, 1, 1, 1])
        with col1:
            file_data = st.file_uploader(label="",
                                         type=["csv", "xlsx"],
                                         accept_multiple_files=False,
                                         # label_visibility="collapsed"
                                         )
        with col2:
            show_code = st.checkbox("显示代码", value=True)
            start_analysis = st.button("开始分析")
        with col3:
            save_charts = st.checkbox("保存图表")
        with col4:
            charts_description = st.checkbox("图表描述", value=True)
        if file_data is None:
            self.report_demo()
        else:
            data_frame = pd.read_csv(file_data, index_col=0) if file_data.name.endswith(".csv") else pd.read_excel(
                file_data, engine="openpyxl")
            df_head = data_frame.head()
            st.dataframe(df_head, )
            num_rows, num_columns = data_frame.shape
            self.prompts = Prompts(num_rows=num_rows, num_cols=num_columns, df_head=df_head)
            highlight_prompt = self.prompts.generate_highlight_prompt()
            print("建议生成中...")
            if start_analysis:
                if self.azure_ai:
                    assert self.azure_api_key, "Azure Api Key 不能为空"
                    assert self.azure_endpoint, "Azure Endpoint 不能为空"
                    assert self.azure_version, "Azure Version 不能为空"
                    openai.api_key = self.azure_api_key
                    openai.api_base = self.azure_endpoint
                    openai.api_version = self.azure_version
                else:
                    assert self.openai_api_key, "OpenAI Api Key 不能为空"
                    cfg.USE_AZURE_AI = False
                    openai.api_key = self.openai_api_key_text
                with st.spinner("正在根据您的数据生成数据分析建议……"):
                    highlight_response = utils.gpt(highlight_prompt)
                    suggestions_list = self._get_suggestion(highlight_response)
                for each_suggestion in suggestions_list:
                    try:
                        with st.spinner(f"正在根据建议：`{each_suggestion}`生成数据分析图表……"):
                            item = {"suggestion": each_suggestion}
                            code_prompt = self.prompts.generate_python_code_prompt_by_suggestion(each_suggestion)
                            code = self.generate_code(code_prompt)
                            if show_code:
                                print(self.global_params.get("code", ""))
                                with st.expander("查看代码", expanded=False):
                                    st.code(code)
                            self.global_params["suggestion"] = each_suggestion
                            self.global_params.update({"suggestion": each_suggestion, "code": code})
                            print("代码执行中...")
                            json_str_result = self.run_code(code, data_frame)
                            with st.expander("查看数据", expanded=False):
                                st.write(json.loads(json_str_result))
                            st_echarts(options=json.loads(json_str_result), height="600px", width="100%")
                            if save_charts and json_str_result:
                                self.save_charts_json(json_str_result)
                                print(f"图表已保存至")
                        if charts_description and json_str_result:
                            with st.spinner(f"正在根据数据图表总结描述信息……"):
                                stats_data = get_stats_data(json_str_result)
                                stats_data = stats_data if stats_data else {}
                                item.update({"title": stats_data.get("title", "")})
                                description_prompt = self.prompts.generate_charts_description_prompt(**stats_data)
                                description_response = utils.gpt(description_prompt)
                                descriptions = self._get_description(description_response)
                                print(f"图表描述：{descriptions}")
                                st.markdown(descriptions, unsafe_allow_html=True)
                                item.update({"description": descriptions})
                                stats_data.pop("description", None)
                                utils.log(f"图表描述：{descriptions}")
                        else:
                            descriptions = ""
                        self.reports.append(item)
                    except Exception as e:
                        print(f"Unable to run code for suggestion: {each_suggestion}, error: {e}")
                        st.error(f"很抱歉，无法为您生成该建议:`{each_suggestion}`图表")
                        with st.expander("查看错误信息", expanded=False):
                            st.write(e)
                        continue
                st.success("数据分析完成")


# def markdown_to_pdf():
#     import markdown
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     from reportlab.lib.styles import getSampleStyleSheet
#     from reportlab.platypus import SimpleDocTemplate, Paragraph
#     html = markdown.markdown("## Markdown to PDF \n\n **Hello world!** \n\n ```python print('Hello world!') ``` ![](https://picsum.photos/200/300) ![test link](https://picsum.photos/200/300)")
#     print(html)
#     doc = SimpleDocTemplate("markdown.pdf", pagesize=letter)
#     styles = getSampleStyleSheet()
#     elements = []
#     elements.append(Paragraph(html, styles['Normal']))
#     doc.build(elements)
#     print("print finished!!")


if __name__ == '__main__':
    client = AiDataAnalysisFrontend()
    # client.report_demo()
    client.report()
