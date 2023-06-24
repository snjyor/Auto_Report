"""
All configs for the project are defined here.
"""
import openai
import os


openai.api_key = os.getenv("OPENAI_API_KEY", "")
USE_AZURE_AI = True
if USE_AZURE_AI:
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

AZURE_GPT_ENGINE = "gpt35"
MAX_TOKENS = 4096



