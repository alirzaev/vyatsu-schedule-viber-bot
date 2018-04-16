from viberbot.api.messages import (
    TextMessage,
    RichMediaMessage
)
from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberSubscribedRequest,
    ViberConversationStartedRequest
)
from viberbot import Api

import keyboards
import requests
from logging import getLogger

URL = 'https://vyatsuscheduleapi.herokuapp.com'

logger = getLogger()


def process_subscribe_request(request: ViberSubscribedRequest, bot: Api):
    bot.send_messages(request.user.id, [
        keyboards.GREETING
    ])


def process_conversation_started_request(request: ViberConversationStartedRequest, bot: Api):
    process_subscribe_request(request, bot)


def process_message_request(request: ViberMessageRequest, bot: Api):
    message = request.message
    logger.info('Processing message request: {}'.format(message.text))

    if message.text not in ['calls', 'schedule_url']:
        bot.send_messages(request.sender.id, [
            TextMessage(text='Не понял'),
            keyboards.GREETING
        ])
        return

    if message.text == 'calls':
        data = requests.get(URL + '/vyatsu/calls').json()
        calls = \
            'Звонки:\n' + \
            '\n'.join('{}) {} - {}'.format(i + 1, b, e) for i, (b, e) in enumerate(data))

        bot.send_messages(request.sender.id, [
            TextMessage(text=calls),
            keyboards.GREETING
        ])
    elif message.text == 'schedule_url':
        bot.send_messages(request.sender.id, [
            TextMessage(text='Еще не умею'),
            keyboards.GREETING
        ])
