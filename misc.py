import logging
from os import getenv
from visit import store_action
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


def log_to_mongo(fun):
    def wrapper(request, command, bot):
        res = None
        user_id = request.sender.id
        action = command['action']
        data = dumps(command.get('data', dict()), ensure_ascii=False)

        try:
            res = fun(request, command, bot)
        finally:
            store_action(user_id, action, data)

        return res

    return wrapper
