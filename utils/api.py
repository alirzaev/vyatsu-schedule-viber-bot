from os import getenv

from aiohttp.client import request

_API_URL = getenv('API_URL')


async def get_groups():
    async with request('GET', f'{_API_URL}/api/v2/groups/by_faculty') as response:
        response.raise_for_status()

        return await response.json()


async def get_season():
    async with request('GET', f'{_API_URL}/api/v2/season/current') as response:
        response.raise_for_status()

        return (await response.json())['season']


async def get_schedule(group_id: str, season: str):
    async with request('GET', f'{_API_URL}/api/v2/schedule/{group_id}/{season}') as response:
        response.raise_for_status()

        return await response.json()


async def get_calls():
    async with request('GET', f'{_API_URL}/api/v2/calls') as response:
        response.raise_for_status()

        return await response.json()
