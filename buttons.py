from viberbot.api.messages import TextMessage


d = {
    "DefaultHeight": True,
    "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [{
        "Columns": 6,
        "Rows": 1,
        # "BgColor": "#2db9b9",
        "ActionType": "reply",
        "ActionBody": "test button",
        "Text": "Нажми меня",
        "TextVAlign": "middle",
        "TextHAlign": "center",
        "TextOpacity": 60,
        "TextSize": "regular"
    }]
}

TEST = TextMessage(text="Ура!", keyboard=d)

GREETING = TextMessage(
    text='Выберите действие',
    keyboard={
        "DefaultHeight": True,
        "BgColor": "#FFFFFF",
        "Type": "keyboard",
        "Buttons": [
            {
                "Columns": 6,
                "Rows": 1,
                "BgColor": "#2db9b9",
                "ActionType": "reply",
                "ActionBody": "calls",
                "Text": "Звонки",
                "TextVAlign": "middle",
                "TextHAlign": "center",
                "TextOpacity": 60,
                "TextSize": "regular"
            },
            {
                "Columns": 6,
                "Rows": 1,
                "BgColor": "#2db9b9",
                "ActionType": "reply",
                "ActionBody": "url",
                "Text": "Посмотреть на сайте",
                "TextVAlign": "middle",
                "TextHAlign": "center",
                "TextOpacity": 60,
                "TextSize": "regular"
            },
        ]
    }
)
