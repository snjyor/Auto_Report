import logging

import tiktoken
from regex import regex
import openai
from with_timeout import with_timeout
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


def choose_better_engine(token_usage):
    """
    Choose a better engine
    :param token_usage: token usage
    :return: engine
    """
    better_engines = ["gpt4-8k", "gpt4-32k"]
    for each in better_engines:
        if cfg.ENGINE_TOKENS_MAPPING.get(each) > token_usage:
            cfg.AZURE_GPT_ENGINE = each
            cfg.MAX_TOKENS = cfg.ENGINE_TOKENS_MAPPING.get(cfg.AZURE_GPT_ENGINE)
            break


# @with_timeout(30)
def gpt(message):
    if isinstance(message, str):
        message = [add_message(message=message, role="user")]
    token_usage = token_usage_from_messages(message)
    if token_usage > cfg.MAX_TOKENS:
        choose_better_engine(token_usage)

    if cfg.USE_AZURE_AI:
        response = openai.ChatCompletion.create(
            engine=cfg.AZURE_GPT_ENGINE,
            messages=message,
            temperature=0.5,
            max_tokens=cfg.MAX_TOKENS,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=cfg.STREAM
        )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            temperature=0.5,
            max_tokens=cfg.MAX_TOKENS,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=cfg.STREAM
        )
    if cfg.STREAM:
        content = response.get("choices")[0]['delta'].get('content', '')
    else:
        content = response['choices'][0].get("message").get("content", '')
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


def get_now_timestamp():
    """
    Get now timestamp
    :return: timestamp
    """
    import time
    return int(time.time())


def token_usage(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))


def token_usage_from_messages(messages, model="gpt35"):
    mapping = {
        "gpt35": "gpt-3.5-turbo-0301",
        "gpt4-8k": "gpt-4-0314",
        "gpt4-32k": "gpt-4-0314",
    }
    encoding = tiktoken.encoding_for_model(mapping.get(model, model))
    if real_model := mapping.get(model):
        return token_usage_from_messages(messages, real_model)
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

