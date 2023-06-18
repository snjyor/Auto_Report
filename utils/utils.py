import logging


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









