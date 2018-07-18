from aiohttp.client import request


def text_message(text: str) -> dict:
    return {
        'type': 'text',
        'text': text
    }


def url_message(media: str) -> dict:
    return {
        'type': 'url',
        'media': media
    }


def keyboard_message(keyboard: dict) -> dict:
    return {
        'keyboard': keyboard
    }


class AsyncApi:

    _SET_WEBHOOK_URL = 'https://chatapi.viber.com/pa/set_webhook'

    _SEND_MESSAGE_URL = 'https://chatapi.viber.com/pa/send_message'

    def __init__(self, auth_token, name):
        self._token = auth_token
        self._name = name
        self._headers = {
            'X-Viber-Auth-Token': self._token
        }

    async def set_webhook(self, url, event_types):
        payload = {
            'url': url,
            'auth_token': self._token,
            'is_inline': False,
            'event_types': event_types
        }

        async with request(
            method='POST',
            url=self._SET_WEBHOOK_URL,
            json=payload,
            headers=self._headers
        ) as response:
            result = await response.json()

            if not result['status'] == 0:
                raise Exception(
                    "failed with status: {0}, message: {1}".format(result['status'], result['status_message']))

            return result['event_types']

    async def send_messages(self, to, messages):
        if not isinstance(messages, list):
            messages = [messages]

        tokens = []

        for message in messages:
            token = await self._send_message(to, message)
            tokens.append(token)

        return tokens

    async def _send_message(self, to, message):
        payload = {
            'auth_token': self._token,
            'receiver': to,
            'sender': {
                'name': self._name
            }
        }
        payload.update(message)

        async with request(
            method='POST',
            url=self._SEND_MESSAGE_URL,
            json=payload,
            headers=self._headers
        ) as response:
            result = await response.json()

            if not result['status'] == 0:
                raise Exception(
                    u"failed with status: {0}, message: {1}".format(result['status'], result['status_message']))

            return result['message_token']

