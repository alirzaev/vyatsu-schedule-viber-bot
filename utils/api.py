import requests
from os import getenv
from typing import List, Dict


_API_URL = getenv('API_URL')


def get_groups() -> List[Dict]:
    response = requests.get(f'{_API_URL}/api/v2/groups/by_faculty')
    response.raise_for_status()

    return response.json()


def get_season() -> str:
    response = requests.get(f'{_API_URL}/api/v2/season/current')
    response.raise_for_status()

    return response.json()['season']


def get_schedule(group_id: str, season: str) -> Dict:
    response = requests.get(f'{_API_URL}/api/v2/schedule/{group_id}/{season}')
    response.raise_for_status()

    return response.json()


def get_calls() -> List:
    response = requests.get(f'{_API_URL}/api/v2/calls')
    response.raise_for_status()

    return response.json()
