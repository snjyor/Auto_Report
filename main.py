import openai
import ast
import io
import logging
import re
import sys
import uuid
from contextlib import redirect_stdout
from typing import List, Optional, Union

import astor
import pandas as pd
from pathlib import Path
ABS_PATH = Path(__file__).parent.absolute()
sys.path.append(str(ABS_PATH))

from utils import utils
from prompts import Prompts
from configs import configs as cfg


class AIAnalyse:

    def __init__(self, llm=None, save_charts=False):
        self._llm = llm
        self._save_charts = save_charts

    def run(self, data_frame: pd.DataFrame, prompt: str, show_code: Optional[bool] = False):
        df_head = data_frame.head()
        num_rows, num_columns = data_frame.shape
        prompts = Prompts(num_rows=num_rows, num_cols=num_columns, df_head=df_head)
        highlight_prompt = prompts.generate_highlight_prompt()
        print(highlight_prompt)
        highlight_response = utils.gpt(highlight_prompt)
        highlight_list = utils.str_to_list_by(highlight_response, split="\n")
        for each_highlight in highlight_list:
            code_prompt = prompts.generate_python_code_prompt_by_suggestion(each_highlight)
            code_response = utils.gpt(code_prompt)
            code = self._get_code(code_response)

        if show_code:
            print(code)
        if self._save_charts:
            code = utils.save_chart(code, folder_name="charts")

    def __call__(self, data_frame: pd.DataFrame, prompt: str, show_code: Optional[bool] = False):
        return self.run(data_frame=data_frame, prompt=prompt, show_code=show_code)

    def run_code(self, code):
        pass

    def _get_code(self, gpt_response: str, separator: str = "```") -> str:
        code = gpt_response
        match = re.search(
            rf"{cfg.START_CODE_TAG}(.*)({cfg.END_CODE_TAG}|{cfg.END_CODE_TAG.replace('<', '</')})",
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


if __name__ == '__main__':
    client = AIAnalyse()
    df = pd.read_csv("test/data/as_macro_cnbs.csv")
    client.run(data_frame=df, prompt="")



