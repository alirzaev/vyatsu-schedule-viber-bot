import re
from json import loads, JSONDecodeError
from typing import Optional


from asyncviberbot import AsyncApi, text_message, url_message
from utils import api, keyboards, logs
from models import user_info
from utils.logs import log_to_mongo

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


async def _get_groups_info():
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

    data = await api.get_groups()
    info = {
        _get_faculty_info(item)['faculty_name']: _get_faculty_info(item)['faculty_info'] for item in data
    }

    return info


_GROUPS_INFO: dict = None

_SEASON: str = None


async def init():
    global _GROUPS_INFO
    global _SEASON

    _GROUPS_INFO = await _get_groups_info()
    _SEASON = await api.get_season()


def _parse_action(action: str) -> Optional[dict]:
    try:
        return loads(action)
    except JSONDecodeError:
        return None


async def _action_calls(request: dict, command: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        keyboards.GREETING
    ])

    data = await api.get_calls()
    calls = \
        'Звонки:\n' + \
        '\n'.join(f"{i}) {rng['start']} - {rng['end']}" for i, rng in enumerate(data, 1))

    await bot.send_messages(request['sender']['id'], [
        text_message(text=calls),
        keyboards.GREETING
    ])


async def _action_select_group(request: dict, command: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        text_message(text='Выберите факультет')
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

    await bot.send_messages(request['sender']['id'], [
        keyboards.create_keyboard(faculty_buttons)
    ])


async def _action_select_faculty(request: dict, command: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        text_message(text='Выберите напрвление')
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

    await bot.send_messages(request['sender']['id'], [
        keyboards.create_keyboard(spec_buttons)
    ])


async def _action_select_spec(request: dict, command: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        text_message(text='Выберите курс')
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

    await bot.send_messages(request['sender']['id'], [
        keyboards.create_keyboard(course_buttons)
    ])


async def _action_select_course(request: dict, command: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        text_message(text='Выберите группу')
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

    await bot.send_messages(request['sender']['id'], [
        keyboards.create_keyboard(group_buttons)
    ])


async def _action_select_group_id(request: dict, command: dict, bot: AsyncApi):
    group_id = command['data']['group_id']
    group_name = command['data']['group_name']

    await user_info.set_selected_group_id(request['sender']['id'], group_id)

    await bot.send_messages(request['sender']['id'], [
        text_message(text=f'Отлично! Ваша группа: {group_name}'),
        keyboards.GREETING
    ])


async def _action_schedule_url(request: dict, command: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        keyboards.GREETING
    ])

    group_id = await user_info.get_selected_group_id(request['sender']['id'])

    await bot.send_messages(request['sender']['id'], [
        url_message(media=f'https://vyatsuschedule.ru/#/schedule/{group_id}/{_SEASON}'),
        keyboards.GREETING
    ])


async def _action_schedule_today(request: dict, command: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        keyboards.GREETING
    ])

    group_id = await user_info.get_selected_group_id(request['sender']['id'])
    if group_id is not None:
        data = await api.get_schedule(group_id, _SEASON)
        week_index = data['today']['week']
        day_index = data['today']['dayOfWeek']
        lessons = data['weeks'][week_index][day_index]

        if all(lesson.strip() == '' for lesson in lessons):
            text = 'Занятий сегодня нет'
        else:
            text = '\n'.join(
                f'{i}) {lesson}' for i, lesson in enumerate(lessons, 1) if lesson.strip() != ''
            )

        await bot.send_messages(request['sender']['id'], [
            text_message(text=text),
            keyboards.GREETING
        ])
    else:
        await bot.send_messages(request['sender']['id'], [
            text_message(text='Выберите сначала группу'),
            keyboards.GREETING
        ])


async def _on_exception(request: dict, bot: AsyncApi):
    await bot.send_messages(request['sender']['id'], [
        text_message(text='Упс, ошибка вышла :('),
        keyboards.GREETING
    ])


async def process_subscribe_request(request: dict, bot: AsyncApi):
    _logger.info(f"Processing subscribe request from {request['user']['id']}")
    await bot.send_messages(request['user']['id'], [
        keyboards.GREETING
    ])


async def process_conversation_started_request(request: dict, bot: AsyncApi):
    _logger.info(f"Processing conversation started request from {request['user']['id']}")
    await bot.send_messages(request['user']['id'], [
        keyboards.GREETING
    ])


async def process_message_request(request: dict, bot: AsyncApi):
    message = request['message']
    _logger.info(f"Processing message request: {message['text']} from {request['sender']['id']}")
    command = _parse_action(message['text'])

    if command is None:
        await bot.send_messages(request['sender']['id'], [
            text_message(text='Не понял'),
            keyboards.GREETING
        ])
        return

    action = command['action']

    try:
        if action == _ACTIONS.CALLS:
            await _action_calls(request, command, bot)
        elif action == _ACTIONS.SELECT_GROUP:
            await _action_select_group(request, command, bot)
        elif action == _ACTIONS.SELECT_FACULTY:
            await _action_select_faculty(request, command, bot)
        elif action == _ACTIONS.SELECT_SPEC:
            await _action_select_spec(request, command, bot)
        elif action == _ACTIONS.SELECT_COURSE:
            await _action_select_course(request, command, bot)
        elif action == _ACTIONS.SELECT_GROUP_ID:
            await _action_select_group_id(request, command, bot)
        elif action == _ACTIONS.SCHEDULE_URL:
            await _action_schedule_url(request, command, bot)
        elif action == _ACTIONS.SCHEDULE_TODAY:
            await _action_schedule_today(request, command, bot)
    except Exception as ex:
        _logger.exception('Error occurred during request processing', exc_info=ex)
        await _on_exception(request, bot)
    finally:
        await log_to_mongo(request, command)
