from viberbot.api.messages import KeyboardMessage

from buttons import BUTTON_CALLS, BUTTON_SCHEDULE_URL, BUTTON_SELECT_GROUP

GREETING = KeyboardMessage(
    keyboard={
        "DefaultHeight": True,
        "BgColor": "#FFFFFF",
        "Type": "keyboard",
        "Buttons": [
            BUTTON_CALLS,
            BUTTON_SELECT_GROUP,
            BUTTON_SCHEDULE_URL
        ]
    }
)
