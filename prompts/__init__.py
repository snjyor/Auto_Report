from datetime import date
import pandas as pd


class Prompts:
    def __init__(self, num_rows: int, num_cols: int, df_head: pd.DataFrame):
        self._args = {
            "today_date": date.today(),
            "num_rows": num_rows,
            "num_cols": num_cols,
            "df_head": df_head
        }
        self.base_prompt = "今天是{today_date},现在我提供给你一个{num_rows}行{num_cols}列的pandas dataframe（df）,下面是这个数据的`print(df.head(5)`):\n```\n{df_head}\n```\n"

    def generate_highlight_prompt(self):
        return (self.base_prompt + "现在我需要对这份数据进行多维度的分析，请列出不同维度间的可视化建议，以便我能够对你列出的每个点进行可视化作图：").format(**self._args)

    def generate_python_code_prompt_by_suggestion(self, suggestion: str):
        self._args.update(dict(suggestion=suggestion))
        return (self.base_prompt + "现在我给你一个画图建议，用于可视化这份数据，你需要将你的画图代码放在{START_CODE_TAG}和{END_CODE_TAG}之间，以便我能够找到你的代码。画图建议如下：\n```{suggestion}```").format(**self._args)



