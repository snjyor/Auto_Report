import json
import os
import sys
from pathlib import Path

import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_echarts

ABS_PATH = Path(__file__).parent.absolute()
sys.path.append(str(ABS_PATH))

from analyse.ai_analyse import AIAnalyse


json_data = []
for root, paths, names in os.walk('export'):
    for name in names:
        if name.endswith('.json'):
            with open(os.path.join(root, name), 'r') as f:
                json_data.append(f.read())

app = Dash(__name__)

app.layout = html.Div([
    html.Button("Upload Data", id="upload_button"),
    html.Button("Generate Data Analyse", id="next_button"),
    html.Div([], id="sub_div"),
], id="main_div")

@app.callback(
    Output("main_div", "children"),
    Input("upload_button", "n_clicks")
)
def upload_file(n_clicks):
    if n_clicks:
        client = AIAnalyse()
        df = pd.read_csv(os.path.join(ABS_PATH, "test/data/as_macro_cnbs.csv"), index_col=0)
        generater = client.run(data_frame=df)
images = []
@app.callback(
    Output("sub_div", "children"),
    Input("next_button", "n_clicks")
)
def update_image(n_clicks):
    while n_clicks:
        for item in globals().get("generater"):
            images.append(dash_echarts.DashECharts(option=json.loads(item), id="echarts", style={"width": f"{100}%", "height": f"{400}%"}))
            return images
        


if __name__ == '__main__':
    app.run_server(debug=True)
