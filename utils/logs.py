import logging
from os import getenv
from models.visit import store_action
from json import dumps


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


async def log_to_mongo(request, command):
        user_id = request['sender']['id']
        action = command['action']
        data = dumps(command.get('data', dict()), ensure_ascii=False)

        await store_action(user_id, action, data)
