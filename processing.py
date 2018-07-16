import re
from json import loads, JSONDecodeError
from typing import Optional

from viberbot import Api
from viberbot.api.messages import (
    TextMessage,
    URLMessage
)
from viberbot.api.viber_requests import (
    ViberMessageRequest,
    ViberSubscribedRequest,
    ViberConversationStartedRequest
)

from utils import api, keyboards, logs
from models import user_info

_logger = logs.get_logger('bot-processing')


class _ACTIONS:
    CALLS = 'calls'
    SELECT_GROUP = 'select_group'
    SELECT_FACULTY = 'select_faculty'
    SELECT_SPEC = 'select_spec'
    SELECT_COURSE = 'select_course'
    SELECT_GROUP_ID = 'select_group_id'
    SCHEDULE_URL = 'schedule_url'
    SCHEDULE_TODAY = 'schedule_today'


def _get_groups_info():
    def _get_group_info(item: dict) -> tuple:
        group_id = item['id']
        group_name = item['name']

        m = re.search(r'(\w+)-(\d+)-\d+-\d+', group_name)
        spec = m.group(1)[:-1]
        course = m.group(2)[0]

        return group_id, group_name, spec, course

    def _get_faculty_shorthand(faculty_name: str) -> str:
        try:
            i = faculty_name.index('(')
            return faculty_name[:i].strip()
        except ValueError:
            return faculty_name

    def _get_faculty_info(item: dict) -> dict:
        faculty_name = item['faculty']
        faculty_shorthand = _get_faculty_shorthand(faculty_name)
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
            'faculty_name': faculty_shorthand,
            'faculty_info': faculty_info
        }

    data = api.get_groups()
    info = {
        _get_faculty_info(item)['faculty_name']: _get_faculty_info(item)['faculty_info'] for item in data
    }

    return info


_GROUPS_INFO = _get_groups_info()

_SEASON = api.get_season()


def _parse_action(action: str) -> Optional[dict]:
    try:
        return loads(action)
    except JSONDecodeError:
        return None


@logs.log_to_mongo
def _action_calls(request: ViberMessageRequest, command: dict, bot: Api):
    bot.send_messages(request.sender.id, [
        keyboards.GREETING
    ])

    data = api.get_calls()
    calls = \
        'Звонки:\n' + \
        '\n'.join(f"{i}) {rng['start']} - {rng['end']}" for i, rng in enumerate(data, 1))

    bot.send_messages(request.sender.id, [
        TextMessage(text=calls),
        keyboards.GREETING
    ])


@logs.log_to_mongo
def _action_select_group(request: ViberMessageRequest, command: dict, bot: Api):
    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите факультет')
    ])

    faculty_buttons = [
        keyboards.create_button(
            3,
            faculty_name,
            {
                'action': _ACTIONS.SELECT_FACULTY,
                'data': {
                    'faculty_name': faculty_name
                }
            }
        ) for faculty_name in sorted(_GROUPS_INFO.keys())
    ]

    bot.send_messages(request.sender.id, [
        keyboards.create_keyboard(faculty_buttons)
    ])


@logs.log_to_mongo
def _action_select_faculty(request: ViberMessageRequest, command: dict, bot: Api):
    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите напрвление')
    ])

    faculty_name = command['data']['faculty_name']

    spec_buttons = [
        keyboards.create_button(
            2,
            spec,
            {
                'action': _ACTIONS.SELECT_SPEC,
                'data': {**command['data'], **{'spec': spec}}
            }
        ) for spec in sorted(_GROUPS_INFO[faculty_name].keys())
    ]

    bot.send_messages(request.sender.id, [
        keyboards.create_keyboard(spec_buttons)
    ])


@logs.log_to_mongo
def _action_select_spec(request: ViberMessageRequest, command: dict, bot: Api):
    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите курс')
    ])

    faculty_name = command['data']['faculty_name']
    spec = command['data']['spec']

    course_buttons = [
        keyboards.create_button(
            2,
            course,
            {
                'action': _ACTIONS.SELECT_COURSE,
                'data': {**command['data'], **{'course': course}}
            }
        ) for course in sorted(_GROUPS_INFO[faculty_name][spec].keys())
    ]

    bot.send_messages(request.sender.id, [
        keyboards.create_keyboard(course_buttons)
    ])


@logs.log_to_mongo
def _action_select_course(request: ViberMessageRequest, command: dict, bot: Api):
    bot.send_messages(request.sender.id, [
        TextMessage(text='Выберите группу')
    ])

    faculty_name = command['data']['faculty_name']
    spec = command['data']['spec']
    course = command['data']['course']

    group_buttons = [
        keyboards.create_button(
            3,
            group['name'],
            {
                'action': _ACTIONS.SELECT_GROUP_ID,
                'data': {**command['data'], **{
                    'group_id': group['id'],
                    'group_name': group['name']
                }}
            }
        ) for group in sorted(_GROUPS_INFO[faculty_name][spec][course], key=lambda value: value['name'])
    ]

    bot.send_messages(request.sender.id, [
        keyboards.create_keyboard(group_buttons)
    ])


@logs.log_to_mongo
def _action_select_group_id(request: ViberMessageRequest, command: dict, bot: Api):
    group_id = command['data']['group_id']
    group_name = command['data']['group_name']

    bot.send_messages(request.sender.id, [
        TextMessage(text=f'Отлично! Ваша группа: {group_name}'),
        keyboards.GREETING
    ])

    user_info.set_selected_group_id(request.sender.id, group_id)


@logs.log_to_mongo
def _action_schedule_url(request: ViberMessageRequest, command: dict, bot: Api):
    bot.send_messages(request.sender.id, [
        keyboards.GREETING
    ])

    group_id = user_info.get_selected_group_id(request.sender.id)

    bot.send_messages(request.sender.id, [
        URLMessage(media=f'https://vyatsuschedule.ru/#/schedule/{group_id}/{_SEASON}'),
        keyboards.GREETING
    ])


@logs.log_to_mongo
def _action_schedule_today(request: ViberMessageRequest, command: dict, bot: Api):
    bot.send_messages(request.sender.id, [
        keyboards.GREETING
    ])

    group_id = user_info.get_selected_group_id(request.sender.id)
    if group_id is not None:
        data = api.get_schedule(group_id, _SEASON)
        week_index = data['today']['week']
        day_index = data['today']['dayOfWeek']
        lessons = data['weeks'][week_index][day_index]

        if all(lesson.strip() == '' for lesson in lessons):
            text = 'Занятий сегодня нет'
        else:
            text = '\n'.join(
                f'{i}) {lesson}' for i, lesson in enumerate(lessons, 1) if lesson.strip() != ''
            )

        bot.send_messages(request.sender.id, [
            TextMessage(text=text),
            keyboards.GREETING
        ])
    else:
        bot.send_messages(request.sender.id, [
            TextMessage(text='Выберите сначала группу'),
            keyboards.GREETING
        ])


def _on_exception(request: ViberMessageRequest, bot: Api):
    bot.send_messages(request.sender.id, [
        TextMessage(text='Упс, ошибка вышла :('),
        keyboards.GREETING
    ])


def process_subscribe_request(request: ViberSubscribedRequest, bot: Api):
    _logger.info(f'Processing subscribe request from {request.user.id}')
    bot.send_messages(request.user.id, [
        keyboards.GREETING
    ])


def process_conversation_started_request(request: ViberConversationStartedRequest, bot: Api):
    _logger.info(f'Processing conversation started request from {request.user.id}')
    bot.send_messages(request.user.id, [
        keyboards.GREETING
    ])


def process_message_request(request: ViberMessageRequest, bot: Api):
    message = request.message
    _logger.info(f'Processing message request: {message.text} from {request.sender.id}')
    command = _parse_action(message.text)

    if command is None:
        bot.send_messages(request.sender.id, [
            TextMessage(text='Не понял'),
            keyboards.GREETING
        ])
        return

    action = command['action']

    try:
        if action == _ACTIONS.CALLS:
            _action_calls(request, command, bot)
        elif action == _ACTIONS.SELECT_GROUP:
            _action_select_group(request, command, bot)
        elif action == _ACTIONS.SELECT_FACULTY:
            _action_select_faculty(request, command, bot)
        elif action == _ACTIONS.SELECT_SPEC:
            _action_select_spec(request, command, bot)
        elif action == _ACTIONS.SELECT_COURSE:
            _action_select_course(request, command, bot)
        elif action == _ACTIONS.SELECT_GROUP_ID:
            _action_select_group_id(request, command, bot)
        elif action == _ACTIONS.SCHEDULE_URL:
            _action_schedule_url(request, command, bot)
        elif action == _ACTIONS.SCHEDULE_TODAY:
            _action_schedule_today(request, command, bot)
    except Exception as ex:
        _logger.exception('Error occurred during request processing', exc_info=ex)
        _on_exception(request, bot)
