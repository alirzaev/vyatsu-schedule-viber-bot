import logging
from os import getenv


_DEBUG = getenv('DEBUG', '0')


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if _DEBUG == '1':
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
