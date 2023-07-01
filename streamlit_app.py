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
        st.markdown('AI Data Analysis', unsafe_allow_html=True)
        st.set_page_config(page_title="AIAnalysis", page_icon="🧊", layout="wide")
        st.sidebar.button("Upload File")

    def draw_page(self):
        for root, path, names in os.walk(os.path.join(ABS_PATH, "export")):
            for name in names:
                time.sleep(0.3)
                with open(os.path.join(root, name), "r") as f:
                    content = json.loads(f.read())
                st_echarts(options=content)
                text = st.text_area("The data is from the file: ", value=name)
                st.write(text)


def markdown_to_pdf():
    import markdown
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    html = markdown.markdown("## Markdown to PDF \n\n **Hello world!** \n\n ```python print('Hello world!') ``` ![](https://picsum.photos/200/300) ![test link](https://picsum.photos/200/300)")
    print(html)
    doc = SimpleDocTemplate("markdown.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(html, styles['Normal']))
    doc.build(elements)
    print("print finished!!")


if __name__ == '__main__':
    client = AiDataAnalysisFrontend()
    # client.save_pdf()
    # markdown_to_pdf()
    client.draw_page()
    print("Done!")
