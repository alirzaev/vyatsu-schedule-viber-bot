from os import getenv

from aiohttp import web
import asyncio

import processing
from asyncviberbot import AsyncApi
from utils import logs

PORT = int(getenv('PORT', 8080))
TOKEN = getenv('TOKEN')
WEB_HOOK_URL = getenv('WEB_HOOK_URL')

# Configure logging
logger = logs.get_logger('bot-main')

viber = AsyncApi(
    name='VyatSU Bot',
    auth_token=TOKEN
)

routes = web.RouteTableDef()


@routes.post('/')
async def incoming(request: web.Request):
    viber_request = await request.json()
    event_type = viber_request['event']

    if event_type == 'message':
        await processing.process_message_request(viber_request, viber)
    elif event_type == 'conversation_started':
        await processing.process_conversation_started_request(viber_request, viber)
    elif event_type == 'subscribed':
        await processing.process_subscribe_request(viber_request, viber)
    elif event_type == 'failed':
        logger.warning('client failed receiving message. failure: {0}'.format(viber_request))

    return web.Response()


async def on_startup():
    asyncio.sleep(5)
    await viber.set_webhook(WEB_HOOK_URL, [
        'message',
        'subscribed',
        'failed',
        'conversation_started'
    ])


async def app_factory():
    await processing.init()

    app = web.Application()
    app.add_routes(routes)

    asyncio.ensure_future(on_startup())

    return app


if __name__ == '__main__':
    web.run_app(app_factory(), port=PORT)
