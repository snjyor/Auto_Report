import logging
from regex import regex
import openai

from configs import configs as cfg


def log(message):
    """
    Log a message
    :param message:
    :return: log info
    """
    handlers = [logging.FileHandler("ai_analysis.log")]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    return logging.getLogger(__name__).info(message)


def gpt(message):
    if isinstance(message, str):
        message = [add_message(message=message, role="user")]
    if cfg.USE_AZURE_AI:
        response = openai.ChatCompletion.create(
            engine=cfg.AZURE_GPT_ENGINE,
            messages=message,
            temperature=0.5,
            max_tokens=cfg.MAX_TOKENS,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            temperature=0.5,
            max_tokens=cfg.MAX_TOKENS,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
    content = response['choices'][0].get("message").get("content")
    return content


def add_message(message, role="user"):
    """
    Add message to the chat
    :param message: message to be added
    :param role: user or system or assistant
    :return: message
    """
    return {"role": role, "content": message}


def str_to_list_by(sentence, split="\n"):
    """
    Split a sentence into a list of sentences by a split
    :param sentence: sentence to be split
    :param split: split
    :return: list of sentences
    """
    return [i for i in sentence.split(split) if i.strip()]


def md5(text):
    """
    Get md5 of a text
    :param text: text
    :return: md5 of the text
    """
    import hashlib
    return hashlib.md5(text.encode()).hexdigest()


def json_regex(text):
    """
    extract json data from a text
    :param text: text
    :return: json string
    """
    try:
        json_pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
        json_match = json_pattern.search(text)
        json_string = json_match.group(0)
    except Exception as err:
        print(f"json_regex error: {err}")
        json_string = ""
    return json_string