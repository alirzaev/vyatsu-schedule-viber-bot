import logging
import datetime


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_current_day(first_date: str) -> tuple:
    today = datetime.date.today()
    d = int(first_date[:2])
    m = int(first_date[2:4])
    y = int(first_date[4:])
    first = datetime.date(y, m, d)

    diff = (today - first).days
    week = diff // 7
    day = diff % 7

    if day > 5: # sunday
        day = (day + 1) % 7
        week = (week + 1) % 2

    return week, day
