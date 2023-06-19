"""
All configs for the project are defined here.
"""
import openai
import os


START_CODE_TAG = "<startCode>"
END_CODE_TAG = "<endCode>"

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
USE_AZURE_AI = True
if USE_AZURE_AI:
    openai.api_type = "azure"
    openai.api_base = ""
    openai.api_version = ""

AZURE_GPT_ENGINE = "gpt35"
MAX_TOKENS = 4096



