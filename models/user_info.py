from typing import Optional

from utils.mongodb_config import get_database

_COLLECTION_NAME = 'user_info'

_database = get_database()


async def get_selected_group_id(user_id: str) -> Optional[str]:
    collection = _database.get_collection(_COLLECTION_NAME)
    item = await collection.find_one({
        'userId': user_id
    })

    if item is None:
        return None
    else:
        return item['groupId']


async def set_selected_group_id(user_id: str, group_id: str):
    collection = _database.get_collection(_COLLECTION_NAME)
    query = {
        'userId': user_id
    }
    item = {
        'userId': user_id,
        'groupId': group_id
    }

    await collection.replace_one(query, item, upsert=True)
