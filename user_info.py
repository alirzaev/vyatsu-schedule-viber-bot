import pymongo
from os import getenv
from typing import Optional

MONGODB_URI = getenv('MONGODB_URI')
_COLLECTION_NAME = 'user_info'

_client = pymongo.MongoClient(MONGODB_URI)
_database_name = _client.database_names()[0]
_database = _client[_database_name]


def get_selected_group_id(user_id: str) -> Optional[str]:
    collection = _database.get_collection(_COLLECTION_NAME)
    item = collection.find_one({
        'userId': user_id
    })

    if item is None:
        return None
    else:
        return item['groupId']


def set_selected_group_id(user_id: str, group_id: str):
    collection = _database.get_collection(_COLLECTION_NAME)
    query = {
        'userId': user_id
    }
    item = {
        'userId': user_id,
        'groupId': group_id
    }

    collection.replace_one(query, item, upsert=True)
