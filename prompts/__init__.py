import json
from datetime import date
import pandas as pd
from configs.constants import *


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
        suggestion_tag = {
            "SUGGESTION_START": SUGGESTION_START,
            "SUGGESTION_END": SUGGESTION_END
        }
        self._args.update(suggestion_tag)
        return (self.base_prompt + "现在我需要对这份数据进行多维度的分析，请列出不同维度间的可视化建议，以便我能够对你列出的每个点进行可视化作图, 每个点以{SUGGESTION_START}开头，以{SUGGESTION_END}结尾。").format(**self._args)

    def generate_python_code_prompt_by_suggestion(self, suggestion: str):
        suggestion_dict = {
            "suggestion": suggestion,
            "START_CODE_TAG": START_CODE_TAG,
            "END_CODE_TAG": END_CODE_TAG
        }
        self._args.update(suggestion_dict)
        return (self.base_prompt + "现在我给你一个画图建议，用于可视化这份数据，当画图建议中有`或`的选择时，请择优选其一种进行画图即可，请使用pyecharts进行绘图，并最后得到echarts_json的数据(标题居中，横纵轴带上单位)；你需要将你的画图代码放在{START_CODE_TAG}和{END_CODE_TAG}之间，以便我能够找到你的代码。画图建议如下：\n```{suggestion}```").format(**self._args)

    def generate_correct_error_prompt(self, suggestion: str, code: str, error_returned: str):
        error_message = {
            "suggestion": suggestion,
            "code": code,
            "error_returned": error_returned,
            "START_CODE_TAG": START_CODE_TAG,
            "END_CODE_TAG": END_CODE_TAG
        }
        self._args.update(error_message)
        return (self.base_prompt + "用户给的画图建议是：```{suggestion}```，你生成的python 代码如下：```{code}```, 这段代码执行后报错信息如下：```{error_returned}```，请纠正这段代码并返回一段新代码(不要导入任何库)以修复上面提到的错误，不要再生成一样的代码，确保代码前面以{START_CODE_TAG}开头，以{END_CODE_TAG}结束").format(**self._args)

    def generate_charts_description_prompt(self, **kwargs):
        charts_description_dict = {
            "DESCRIPTION_START": DESCRIPTION_START,
            "DESCRIPTION_END": DESCRIPTION_END
        }
        charts_description_dict.update(kwargs)
        self._args.update(charts_description_dict)
        return "现在我有一份图表数据，该图表的类型为：`{charts_type}`, 标题为：`{title}`，其X轴名为：`{x_names}`,Y轴名为：`{y_names}`,\n这份图表的图例和对应的数据如下所示：```{name_data_mapping}```, \n这份图表数据的描述性信息pandas dataframe如下所示：```{describe_df}```，\n我需要你对这份图表数据进行总结性分析描述，让我看到你的描述就知道这份图表表明的是什么意思。你需要将你的描述放在{DESCRIPTION_START}和{DESCRIPTION_END}之间，以便我能够找到你的描述。".format(**self._args)



