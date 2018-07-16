import sched
import threading
import time
from os import getenv

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import (
    ViberConversationStartedRequest,
    ViberFailedRequest,
    ViberMessageRequest,
    ViberSubscribedRequest
)

from utils import logs
import processing

PORT = int(getenv('PORT', 8080))
HOST = getenv('IP', '0.0.0.0')
TOKEN = getenv('TOKEN')
WEB_HOOK_URL = getenv('WEB_HOOK_URL')

# Configure logging
logger = logs.get_logger('bot-main')

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='VyatSU Bot',
    avatar='',
    auth_token=TOKEN
))


@app.route('/', methods=['POST'])
def incoming():
    viber_request = viber.parse_request(request.get_data(as_text=True))

    if isinstance(viber_request, ViberMessageRequest):
        processing.process_message_request(viber_request, viber)
    elif isinstance(viber_request, ViberConversationStartedRequest):
        processing.process_conversation_started_request(viber_request, viber)
    elif isinstance(viber_request, ViberSubscribedRequest):
        processing.process_subscribe_request(viber_request, viber)
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warning('client failed receiving message. failure: {0}'.format(viber_request))

    return Response(status=200)


def set_web_hook(bot_instance):
    bot_instance.set_webhook(WEB_HOOK_URL)


scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enter(5, 1, set_web_hook, (viber,))
t = threading.Thread(target=scheduler.run)
t.start()

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
