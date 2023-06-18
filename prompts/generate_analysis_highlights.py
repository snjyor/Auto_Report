from datetime import date
import pandas as pd


class GenerateHighlightsPrompt:
    def __init__(self, num_rows: int, num_cols: int, df_head: pd.DataFrame):
        self._args = {
            "today_date": date.today(),
            "num_rows": num_rows,
            "num_cols": num_cols,
            "df_head": df_head
        }
        self.base_prompt = "今天是{today_date},现在我提供给你一个{num_rows}行{num_cols}列的pandas dataframe（df）,下面是这个数据的`print(df.head(5)`):\n```\n{df_head}\n```\n现在我需要对这份数据进行多维度的分析，请列出不同维度间的可视化建议，以便我能够对你列出的每个点进行可视化作图："

    def __str__(self):
        return self.base_prompt.format(**self._args)

