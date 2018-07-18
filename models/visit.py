import datetime

from utils.mongodb_config import get_database

_COLLECTION_NAME = 'visit'

_database = get_database()


async def store_action(user_id: str, action: str, data: str):
    collection = _database.get_collection(_COLLECTION_NAME)

    await collection.insert_one({
        'viber_id': user_id,
        'action': action,
        'data': data,
        'date': datetime.datetime.now()
    })
