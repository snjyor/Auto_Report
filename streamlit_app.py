import json
import os.path
import sys
import time
from pathlib import Path
import streamlit as st
from streamlit_echarts import st_echarts

ABS_PATH = Path(__file__).parent.absolute()
sys.path.append(str(ABS_PATH))


class AiDataAnalysisFrontend:
    def __init__(self):
        st.set_page_config(page_title="Auto Data Analysis", page_icon="📊", layout="wide")
        st.markdown('<h1 style="text-align: center;">AI Data Analysis</h1>', unsafe_allow_html=True)

    def draw_page(self):
        for root, path, names in os.walk(os.path.join(ABS_PATH, "export")):
            for name in names:
                with open(os.path.join(root, name), "r") as f:
                    content = f.read()
                    option = json.loads(content)
                    st_echarts(option, height="600px", width="100%")
                    st.write(name.split(".")[0])
                    time.sleep(1)


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
    # client.save_pdf()
    # markdown_to_pdf()
    client.draw_page()
    # print("Done!")

