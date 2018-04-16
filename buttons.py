from json import dumps


def create_button(width: int, text: str, action: dict) -> dict:
    return {
        "Columns": width,
        "Rows": 1,
        "BgColor": "#2db9b9",
        "ActionType": "reply",
        "ActionBody": dumps(action, ensure_ascii=False),
        "Text": text,
        "TextVAlign": "middle",
        "TextHAlign": "center",
        "TextOpacity": 60,
        "TextSize": "regular"
    }


BUTTON_CALLS = create_button(3, 'Звонки', {
    'action': 'calls'
})

BUTTON_SCHEDULE_URL = create_button(3, 'Посмотреть на сайте', {
    'action': 'schedule_url'
})

BUTTON_SELECT_GROUP = create_button(3, 'Выбрать группу', {
    'action': 'select_group',
    'data': {}
})

BUTTON_SCHEDULE = create_button(3, 'Расписание', {
    'action': 'schedule_today'
})
