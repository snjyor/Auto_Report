import logging
from configs import configs as cfg
import openai


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

