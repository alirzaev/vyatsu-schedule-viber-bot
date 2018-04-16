from viberbot.api.messages import KeyboardMessage

from buttons import BUTTON_CALLS, BUTTON_SCHEDULE_URL, BUTTON_SELECT_GROUP, BUTTON_SCHEDULE

GREETING = KeyboardMessage(
    keyboard={
        "DefaultHeight": False,
        "BgColor": "#FFFFFF",
        "Type": "keyboard",
        "Buttons": [
            BUTTON_CALLS,
            BUTTON_SCHEDULE,
            BUTTON_SELECT_GROUP,
            BUTTON_SCHEDULE_URL
        ]
    }
)


def create_keyboard(buttons: list) -> KeyboardMessage:
    return KeyboardMessage(
        keyboard={
            "DefaultHeight": False,
            "BgColor": "#FFFFFF",
            "Type": "keyboard",
            "Buttons": buttons
        }
    )
