import re


def beautify_lesson(lesson: str) -> str:
    lesson = re.sub('\r', ' ', lesson)
    lesson = re.sub('Лекция', 'Лек.', lesson)
    lesson = re.sub('Лабораторная работа', 'Лаб.', lesson)
    lesson = re.sub('Практическое занятие', 'Пр.', lesson)
    lesson = re.sub(r'^([А-Яа-я]+-\d{4}-\d{2}-\d{2}, )', '', lesson)
    lesson = re.sub(r'\s?([А-Яа-я]+-\d{4}-\d{2}-\d{2}, )', '; ', lesson)

    return lesson
