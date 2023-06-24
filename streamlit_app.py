import json
import os.path
import sys
from pathlib import Path
import streamlit as st
from streamlit_echarts import st_echarts

ABS_PATH = Path(__file__).parent.absolute()
sys.path.append(str(ABS_PATH))


st.title("AI Data Analysis")
st.write("This is a demo of AI Data Analysis.")

for root, path, names in os.walk(os.path.join(ABS_PATH, "export")):
    for name in names:
        with open(os.path.join(root, name), "r") as f:
            content = json.loads(f.read())
            st_echarts(options=content)

