from json import dumps

from viberbot.api.messages import KeyboardMessage


def create_button(width: int, text: str, action: dict) -> dict:
    return {
        'Columns': width,
        'Rows': 1,
        'BgColor': '#574e92',
        'ActionType': 'reply',
        'ActionBody': dumps(action, ensure_ascii=False),
        'Text': r'<font color="#FFFFFF">{}</font>'.format(text),
        'TextVAlign': 'middle',
        'TextHAlign': 'center',
        'TextOpacity': 90,
        'TextSize': 'regular'
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


BUTTON_HELP = create_button(6, 'Справка', {
    'action': 'help'
})


def create_keyboard(buttons: list) -> KeyboardMessage:
    return KeyboardMessage(
        keyboard={
            'DefaultHeight': False,
            'BgColor': '#FFFFFF',
            'Type': 'keyboard',
            'Buttons': buttons
        }
    )


GREETING = create_keyboard([
    BUTTON_CALLS,
    BUTTON_SCHEDULE,
    BUTTON_SELECT_GROUP,
    BUTTON_SCHEDULE_URL,
    BUTTON_HELP
]
)
