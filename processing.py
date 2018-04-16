from json import loads, JSONDecodeError
from logging import getLogger
from typing import Optional

import requests
from viberbot import Api
from viberbot.api.messages import (
    TextMessage
)
from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberSubscribedRequest,
    ViberConversationStartedRequest
)

import keyboards
import buttons
import re

_URL = 'https://vyatsuscheduleapi.herokuapp.com'

_logger = getLogger()


def _get_groups_info():
    def _get_group_info(item: dict) -> tuple:
        group_id = item['id']
        group_name = item['name']

        m = re.search(r'(\w+)\-(\d+)\-\d+\-\d+', group_name)
        spec = m.group(1)[:-1]
        course = m.group(2)[0]

        return group_id, group_name, spec, course

    def _get_faculty_info(item: dict) -> dict:
        faculty_name = item['faculty']
        groups = item['groups']

        # напрвление, курс, группы
        faculty_info = dict()

        for group in groups:
            group_id, group_name, spec, course = _get_group_info(group)
            if spec not in faculty_info:
                faculty_info[spec] = dict()

            if course not in faculty_info[spec]:
                faculty_info[spec][course] = list()

            faculty_info[spec][course].append({
                'id': group_id,
                'name': group_name
            })

        return {
            'faculty_name': faculty_name,
            'faculty_info': faculty_info
        }

    data = requests.get(_URL + '/vyatsu/v2/groups/by_faculty.json').json()
    info = {
        _get_faculty_info(item)['faculty_name'][:6]: _get_faculty_info(item)['faculty_info'] for item in data
    }

    return info


_GROUPS_INFO = _get_groups_info()


def _parse_action(action: str) -> Optional[dict]:
    try:
        return loads(action)
    except JSONDecodeError:
        return None


def _command_calls(request: ViberMessageRequest, bot: Api):
    data = requests.get(_URL + '/vyatsu/calls').json()
    calls = \
        'Звонки:\n' + \
        '\n'.join('{}) {} - {}'.format(i + 1, b, e) for i, (b, e) in enumerate(data))

    bot.send_messages(request.sender.id, [
        TextMessage(text=calls),
        keyboards.GREETING
    ])


def _command_select_group(request: ViberMessageRequest, bot: Api):
    _logger.info("Processing command 'select_group'")
    faculty_buttons = [
        buttons.create_button(
            3,
            faculty_name,
            {
                'action': 'select_faculty',
                'data': {
                    'faculty_name': faculty_name
                }
            }
        ) for faculty_name in _GROUPS_INFO.keys()
    ]

    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите факультет'),
        keyboards.create_keyboard(faculty_buttons)
    ])


def _command_select_faculty(request: ViberMessageRequest, bot: Api):
    _logger.info("Processing command 'select_faculty'")
    command = _parse_action(request.message.text)
    faculty_name = command['data']['faculty_name']

    command['action'] = 'select_spec'

    spec_buttons = [
        buttons.create_button(
            2,
            spec,
            {
                'action': command['action'],
                'data': {**command['data'], **{'spec': spec}}
            }
        ) for spec in _GROUPS_INFO[faculty_name].keys()
    ]

    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите напрвление'),
        keyboards.create_keyboard(spec_buttons)
    ])


def _command_select_spec(request: ViberMessageRequest, bot: Api):
    _logger.info("Processing command 'select_spec'")
    command = _parse_action(request.message.text)
    faculty_name = command['data']['faculty_name']
    spec = command['data']['spec']

    command['action'] = 'select_course'

    course_buttons = [
        buttons.create_button(
            2,
            course,
            {
                'action': command['action'],
                'data': {**command['data'], **{'course': course}}
            }
        ) for course in _GROUPS_INFO[faculty_name][spec].keys()
    ]

    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите курс'),
        keyboards.create_keyboard(course_buttons)
    ])


def _command_select_course(request: ViberMessageRequest, bot: Api):
    _logger.info("Processing command 'select_course'")
    command = _parse_action(request.message.text)
    faculty_name = command['data']['faculty_name']
    spec = command['data']['spec']
    course = command['data']['course']

    command['action'] = 'select_group_id'

    group_buttons = [
        buttons.create_button(
            3,
            group['name'],
            {
                'action': command['action'],
                'data': {**command['data'], **{'group_id': group['id'], 'group_name': group['name']}}
            }
        ) for group in _GROUPS_INFO[faculty_name][spec][course]
    ]

    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите группу'),
        keyboards.create_keyboard(group_buttons)
    ])


def _command_select_group_id(request: ViberMessageRequest, bot: Api):
    _logger.info("Processing command 'select_group_id'")
    command = _parse_action(request.message.text)

    group_id = command['data']['group_id']
    group_name = command['data']['group_name']

    bot.send_messages(request.sender.id, [
        TextMessage(text='Отлично! Ваша группа: {} ({})'.format(group_name, group_id))
    ])


def process_subscribe_request(request: ViberSubscribedRequest, bot: Api):
    bot.send_messages(request.user.id, [
        keyboards.GREETING
    ])


def process_conversation_started_request(request: ViberConversationStartedRequest, bot: Api):
    process_subscribe_request(request, bot)


def process_message_request(request: ViberMessageRequest, bot: Api):
    message = request.message
    _logger.info('Processing message request: {}'.format(message.text))
    command = _parse_action(message.text)

    if command is None:
        bot.send_messages(request.sender.id, [
            TextMessage(text='Не понял'),
            keyboards.GREETING
        ])
        return

    if command['action'] == 'calls':
        _command_calls(request, bot)
    elif command['action'] == 'select_group':
        _command_select_group(request, bot)
    elif command['action'] == 'select_faculty':
        _command_select_faculty(request, bot)
    elif command['action'] == 'select_spec':
        _command_select_spec(request, bot)
    elif command['action'] == 'select_course':
        _command_select_course(request, bot)
    elif command['action'] == 'select_group_id':
        _command_select_group_id(request, bot)
    elif command['action'] == 'schedule_url':
        bot.send_messages(request.sender.id, [
            TextMessage(text='Еще не умею'),
            keyboards.GREETING
        ])
