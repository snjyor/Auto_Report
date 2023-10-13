import json
import os
import sys
from pathlib import Path
import pandas as pd

ABS_PATH = Path(__file__).parent.parent.absolute()
sys.path.append(str(ABS_PATH))

from configs.constants import *


class StatsData:
    def __init__(self):
        pass

    def __call__(self, json_str_result):
        return self.get_stats_data(json_str_result)

    def get_stats_data(self, json_str_result):
        json_result = json.loads(json_str_result)
        charts_type = json_result.get("series", [])[0].get("type", "")
        type_func_mapping = {
            "bar": self._get_stats_data_from_default,
            "line": self._get_stats_data_from_default,
            "pie": self._get_stats_data_from_pie_chart,
            "scatter": self._get_stats_data_from_default,
            "boxplot": self._get_stats_data_from_boxplot_chart,
            "heatmap": self._get_stats_data_from_heatmap_chart,
            "funnel": self._get_stats_data_from_funnel_chart,
            "radar": self._get_stats_data_from_radar_chart,
            "parallel": self._get_stats_data_from_parallel_chart,
            "sankey": self._get_stats_data_from_sankey_chart,
            "graph": self._get_stats_data_from_graph_chart,
            "tree": self._get_stats_data_from_tree_chart,
            "treemap": self._get_stats_data_from_treemap_chart,
            "sunburst": self._get_stats_data_from_sunburst_chart,
            "map": self._get_stats_data_from_map_chart,
            "kline": self._get_stats_data_from_kline_chart,
            "effectscatter": self._get_stats_data_from_effectscatter_chart,
            "lines": self._get_stats_data_from_lines_chart,
            "scatter3d": self._get_stats_data_from_scatter3d_chart,
            "bar3d": self._get_stats_data_from_bar3d_chart,
            "surface3d": self._get_stats_data_from_surface3d_chart,
            "scattermap": self._get_stats_data_from_scattermap_chart
        }
        result = type_func_mapping.get(charts_type, self._get_stats_data_from_default)(json_result)
        return result

    def _get_stats_data_from_default(self, json_result):
        title = json_result.get("title", [{}])[0].get("text", "")
        series = json_result.get("series", [])
        charts_type = series[0].get("type", "")
        name_data_mapping = {each_series.get("name", ""): each_series.get("data", []) for each_series in series}
        describe_df = {k: pd.DataFrame(v).describe() for k, v in name_data_mapping.items()}
        name_data_mapping = {k: v[:DATA_DETAIL_LIMIT] for k, v in name_data_mapping.items()}
        x_names = [each.get("name", "") for each in json_result.get("xAxis", [{}])]
        y_names = [each.get("name", "") for each in json_result.get("yAxis", [{}])]
        xy_names = [i for i in sum([x_names, y_names], []) if i]
        describe_df = {
            key: value.rename(columns=dict(zip(list(value.columns), y_names)))
            if value.shape[1] == 1
            else value.rename(columns=dict(zip(list(value.columns), xy_names)))
            for key, value in describe_df.items()
        }
        action = {
            "charts_type": charts_type,  # "bar", "line", "pie" .etc
            "title": title,
            "name_data_mapping": name_data_mapping,
            "describe_df": describe_df,  # {"name": pd.DataFrame}
            "x_names": x_names,
            "y_names": y_names
        }
        return action

    def _get_stats_data_from_radar_chart(self, json_result):
        title = json_result.get("title", [{}])[0].get("text", "")
        series = json_result.get("series", [])
        charts_type = series[0].get("type", "")
        name_data_mapping = {each_series.get("name", ""): each_series.get("data", []) for each_series in series}
        describe_df = {k: pd.DataFrame(v).describe() for k, v in name_data_mapping.items()}
        name_data_mapping = {k: v[:DATA_DETAIL_LIMIT] for k, v in name_data_mapping.items()}

        indicator = json_result.get("radar", {}).get("indicator", [{}])
        x_names = [each.get("name", "") for each in indicator]
        describe_df = {k: v.rename(columns=dict(zip(list(v.columns), x_names))) for k, v in describe_df.items()}

        action = {
            "charts_type": charts_type,  # "bar", "line", "pie" .etc
            "title": title,
            "name_data_mapping": name_data_mapping,
            "describe_df": describe_df,  # {"name": pd.DataFrame}
            "x_names": x_names
        }
        return action

    def _get_stats_data_from_pie_chart(self, json_result):
        title = json_result.get("title", [{}])[0].get("text", "")
        series = json_result.get("series", [])
        charts_type = series[0].get("type", "")
        name_data_mapping = {each_series.get("name", ""): each_series.get("data", []) for each_series in series}
        describe_df = {k: pd.DataFrame(v).describe() for k, v in name_data_mapping.items()}
        name_data_mapping = {k: v[:DATA_DETAIL_LIMIT] for k, v in name_data_mapping.items()}
        action = {
            "charts_type": charts_type,  # "bar", "line", "pie" .etc
            "title": title,
            "name_data_mapping": name_data_mapping,
            "describe_df": describe_df  # {"name": pd.DataFrame}
        }
        return action

    def _get_stats_data_from_boxplot_chart(self, json_result):
        pass

    def _get_stats_data_from_heatmap_chart(self, json_result):
        pass

    def _get_stats_data_from_funnel_chart(self, json_result):
        pass

    def _get_stats_data_from_parallel_chart(self, json_result):
        pass

    def _get_stats_data_from_sankey_chart(self, json_result):
        pass

    def _get_stats_data_from_graph_chart(self, json_result):
        pass

    def _get_stats_data_from_tree_chart(self, json_result):
        pass

    def _get_stats_data_from_treemap_chart(self, json_result):
        pass

    def _get_stats_data_from_sunburst_chart(self, json_result):
        pass

    def _get_stats_data_from_map_chart(self, json_result):
        pass

    def _get_stats_data_from_kline_chart(self, json_result):
        pass

    def _get_stats_data_from_effectscatter_chart(self, json_result):
        pass

    def _get_stats_data_from_lines_chart(self, json_result):
        pass

    def _get_stats_data_from_scatter3d_chart(self, json_result):
        pass

    def _get_stats_data_from_bar3d_chart(self, json_result):
        pass

    def _get_stats_data_from_surface3d_chart(self, json_result):
        pass

    def _get_stats_data_from_scattermap_chart(self, json_result):
        pass


get_stats_data = StatsData()

# for root, path, names in os.walk(os.path.join(ABS_PATH, "export")):
#     for name in names:
#         with open(os.path.join(root, name), "r") as f:
#             content = f.read()
#         result = get_stats_data(content)
#         print(result)
