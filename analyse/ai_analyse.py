import json
import ast
import io
import re
import sys
import os
from contextlib import redirect_stdout
from typing import Optional
import astor
import pandas as pd
from pathlib import Path
import pyecharts
import regex

ABS_PATH = Path(__file__).parent.parent.absolute()
sys.path.append(str(ABS_PATH))

from utils import utils
from prompts import Prompts
from configs.constants import *
from analyse.stats_data import get_stats_data


class AIAnalyse:
    def __init__(self):
        self._max_retries = 3
        self.prompts = None
        self.global_params = {}
        self.reports = []

    def run(
        self,
        data_frame: pd.DataFrame,
        save_charts: bool = True,
        show_code: Optional[bool] = True,
        charts_description: Optional[bool] = True,
    ):
        df_head = data_frame.head()
        num_rows, num_columns = data_frame.shape
        self.prompts = Prompts(num_rows=num_rows, num_cols=num_columns, df_head=df_head)
        highlight_prompt = self.prompts.generate_highlight_prompt()
        print("建议生成中...")
        highlight_response = utils.gpt(highlight_prompt)
        suggestions_list = self._get_suggestion(highlight_response)
        for each_suggestion in suggestions_list:
            try:
                print(f"根据以下数据可视化建议进行绘图：{each_suggestion}", end="\n")
                print("代码生成中...")
                item = {"suggestion": each_suggestion}
                code_prompt = self.prompts.generate_python_code_prompt_by_suggestion(
                    each_suggestion
                )
                code = self.generate_code(code_prompt)
                self.global_params["suggestion"] = each_suggestion
                self.global_params.update({"suggestion": each_suggestion, "code": code})
                if show_code:
                    print(self.global_params.get("code", ""))
                print("代码执行中...")
                json_str_result = self.run_code(code, data_frame)
                if save_charts and json_str_result:
                    self.save_charts_json(json_str_result)
                    print(f"图表已保存至{CHARTS_EXPORT_PATH}")
                if charts_description and json_str_result:
                    stats_data = get_stats_data(json_str_result)
                    stats_data = stats_data if stats_data else {}
                    item.update({"title": stats_data.get("title", "")})
                    description_prompt = (
                        self.prompts.generate_charts_description_prompt(**stats_data)
                    )
                    description_response = utils.gpt(description_prompt)
                    print(f"图表描述：{description_response}")
                    descriptions = self._get_description(description_response)
                    print(f"图表描述：{descriptions}")
                    item.update({"description": descriptions})
                    stats_data.pop("description", None)
                    utils.log(f"图表描述：{descriptions}")
                else:
                    descriptions = ""
                self.reports.append(item)
                yield json_str_result, descriptions
            except Exception as e:
                print(
                    f"Unable to run code for suggestion: {each_suggestion}, error: {e}"
                )
                continue
        self._save_report()

    def _save_report(self):
        with open(REPORT_NAME, "w") as f:
            f.write(json.dumps(self.reports, indent=2, ensure_ascii=False))

    def describe_df(self, data_frame: pd.DataFrame):
        for col in data_frame.columns:
            if col in ["level_0", "index"]:
                continue
            if data_frame[col].dtype in [int, float]:
                col_describe = data_frame[col].describe()

    def __call__(
        self,
        data_frame: pd.DataFrame,
        save_charts: Optional[bool] = True,
        show_code: Optional[bool] = True,
        charts_description: Optional[bool] = True,
    ):
        return self.run(
            data_frame=data_frame,
            save_charts=save_charts,
            show_code=show_code,
            charts_description=charts_description,
        )

    def generate_code(self, prompt: str):
        code_response = utils.gpt(prompt)
        code = self._get_code(code_response)
        return code

    def _clean_code(self, code: str) -> str:
        """
        A method to clean the code to prevent malicious code execution
        Args:
            code(str): A python code

        Returns (str): Returns a Clean Code String

        """
        tree = ast.parse(code)

        new_body = []
        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "df"
            ):
                node.value = ast.Name(id="df", ctx=ast.Load())
                node.value.ctx = ast.Load()
            new_body.append(node)

        new_tree = ast.Module(body=new_body)
        return astor.to_source(new_tree).strip()

    def save_charts_json(self, json_str: str = None, folder_name: str = None):
        if not json_str:
            utils.log("Please provide a valid json string")
            return
        json_data = json.loads(json_str)
        file_name = (
            json_data.get("title", [{}])[0]
            .get("text", utils.md5(json_str))
            .replace("/", "_")
            .replace("\\", "_")
        )
        if folder_name:
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)
            export_path = os.path.join(ABS_PATH, f"{folder_name}/{file_name}.json")
        else:
            if not os.path.exists(CHARTS_EXPORT_PATH):
                os.mkdir(CHARTS_EXPORT_PATH)
            export_path = os.path.join(
                ABS_PATH, f"{CHARTS_EXPORT_PATH}/{file_name}.json"
            )
        with open(export_path, "w") as f:
            f.write(json.dumps(json_data, indent=2, ensure_ascii=False))

    def run_code(
        self,
        code: str,
        data_frame: pd.DataFrame,
        use_error_correction_framework: bool = False,
    ) -> str:
        """
        A method to execute the python code generated by LLMs to answer the question about the
        input dataframe. Run the code in the current context and return the result.
        Args:
            code (str): A python code to execute
            data_frame (pd.DataFrame): A full Pandas DataFrame
            use_error_correction_framework (bool): Turn on Error Correction mechanism.
            Default to True

        Returns:

        """
        code_to_run = self._clean_code(code)
        utils.log(
            f"""
            Code running:
            ```
            {code_to_run}
            ```"""
        )
        if data_frame.index.name is not None:
            if data_frame.index.dtype != "int64" or data_frame.index.name != "index":
                data_frame.reset_index(drop=False, inplace=True)
        if "level_0" in data_frame.columns:
            data_frame.drop(columns=["level_0"], inplace=True)
        if "index" in data_frame.columns:
            data_frame.drop(columns=["index"], inplace=True)
        environment = {
            name: getattr(__builtins__, name)
            for name in dir(__builtins__)
            if not name.startswith("_")
        }
        environment.update(
            {"pd": pd, "json": json, "pyecharts": pyecharts, "df": data_frame}
        )

        # Redirect standard output to a StringIO buffer
        with redirect_stdout(io.StringIO()) as output:
            count = 0
            while count < self._max_retries:
                try:
                    exec(code_to_run, environment)
                    code = code_to_run
                    break
                except Exception as err:
                    if not use_error_correction_framework:
                        raise err

                    count += 1
                    fix_error_prompt = self.prompts.generate_correct_error_prompt(
                        suggestion=self.global_params["suggestion"],
                        error_returned=err,
                        code=code,
                    )

                    code_to_run = self.generate_code(fix_error_prompt)

        captured_output = output.getvalue()
        if captured_output:
            try:
                json.loads(captured_output)
            except Exception as err:
                utils.log(
                    f"Unable to parse the output: {captured_output}, error: {err}"
                )
                values = re.findall(r"=.(\{[\s\S]*?);", captured_output)
                captured_output = values[0] if values else ""
            finally:
                if not captured_output:
                    values = re.findall("({[\s\S]*})\n{", captured_output)
                    captured_output = values[0] if values else ""
                if captured_output:
                    return captured_output
        # Evaluate the last line and return its value or the captured output
        lines = code.strip().split("\n")
        last_line = lines[-1].strip()
        try:
            match = re.match(r"^print\((.*)\)$", last_line)
            if match:
                last_line = match.group(1)
            else:
                last_node = ast.parse(last_line).body[0]
                if isinstance(last_node, ast.Assign) and last_node.targets:
                    last_line = last_node.targets[0].id
                elif (
                    isinstance(last_node, ast.Expr)
                    and isinstance(last_node.value, ast.Call)
                    and isinstance(last_node.value.func, ast.Attribute)
                    and last_node.value.func.attr == "render_notebook"
                ):
                    try:
                        value = eval(
                            compile(
                                ast.Expression(last_node.value.args[0]),
                                "<string>",
                                "eval",
                            )
                        )
                    except Exception as err:
                        notebook_data = eval(last_line, environment).data
                        value = re.findall(r"=.(\{[\s\S]*?);", notebook_data)
                        value = value[0] if value else ""
                    return value
            value = eval(last_line, environment)
            try:
                json.loads(value)
            except Exception as err:
                utils.log(f"output value is not json format, detail error: {err}")
                values = re.findall(r"=.(\{[\s\S]*?);", value)
                value = values[0] if values else ""
            return value
        except Exception:
            return captured_output

    def _get_code(self, gpt_response: str, separator: str = "```") -> str:
        code = gpt_response
        match = re.search(
            rf"{START_CODE_TAG}(.*)({END_CODE_TAG}|{END_CODE_TAG.replace('<', '</')})",
            code,
            re.DOTALL,
        )
        if match:
            code = match.group(1).strip()
        if len(code.split(separator)) > 1:
            code = code.split(separator)[1]
        code = self._polish_code(code)
        if not self._is_python_code(code):
            raise utils.log("Invalid Python Code")
        return code

    def _get_suggestion(self, gpt_response: str) -> str:
        gpt_response = gpt_response.replace("\n", "")
        suggestion_pattern = regex.compile(rf"{SUGGESTION_START}(.*?){SUGGESTION_END}")
        suggestions = suggestion_pattern.findall(gpt_response)
        return suggestions

    def _get_description(self, description_response):
        description_pattern = regex.compile(
            rf"{DESCRIPTION_START}([\s\S]*?)({DESCRIPTION_END}|{DESCRIPTION_END.replace('<','</')})",
            re.DOTALL,
        )
        descriptions = description_pattern.search(description_response)
        if descriptions:
            descriptions = descriptions.group(1).strip()
        else:
            descriptions = description_response
        return descriptions

    def _polish_code(self, code: str) -> str:
        """
        Polish the code by removing the leading "python" or "py",  \
        removing the imports and removing trailing spaces and new lines.

        Args:
            code (str): Code

        Returns:
            str: Polished code
        """
        if re.match(r"^(python|py)", code):
            code = re.sub(r"^(python|py)", "", code)
        if re.match(r"^`.*`$", code):
            code = re.sub(r"^`(.*)`$", r"\1", code)
        code = code.strip()
        return code

    def _is_python_code(self, string):
        """
        Return True if it is valid python code.
        Args:
            string (str):

        Returns (bool): True if Python Code otherwise False

        """
        try:
            ast.parse(string)
            return True
        except SyntaxError:
            return False


if __name__ == "__main__":
    client = AIAnalyse()
    df = pd.read_csv(os.path.join(ABS_PATH, "test/data/as_macro_cnbs.csv"), index_col=0)
    generater = client(data_frame=df)
    for item in generater:
        print()
    print("DDDDDONEEEE!!!")
    # for root, path, names in os.walk(os.path.join(ABS_PATH, "export")):
    #     for name in names:
    #         with open(os.path.join(root, name), "r") as f:
    #             content = f.read()
    #         client.get_stats_data(content)
    #         print()
