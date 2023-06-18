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

from utils import utils


class AIAnalyse:

    def __init__(self, llm=None, save_charts=False):
        self._llm = llm
        self._save_charts = save_charts

    def run(self, data_frame: pd.DataFrame, prompt: str, show_code: Optional[bool] = False):
        df_head = data_frame.head()
        num_rows, num_columns = data_frame.shape
        code = self._get_code(prompt=prompt)
        if show_code:
            print(code)
        if self._save_charts:
            code = utils.save_chart(code, folder_name="charts")

    def __call__(self, data_frame: pd.DataFrame, prompt: str, show_code: Optional[bool] = False):
        return self.run(data_frame=data_frame, prompt=prompt, show_code=show_code)

    def run_code(self, code):
        pass

    def _get_code(self, prompt: str) -> str:
        pass


