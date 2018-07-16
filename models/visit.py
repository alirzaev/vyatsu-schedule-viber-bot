import pymongo
from os import getenv
import datetime

MONGODB_URI = getenv('MONGODB_URI')
_COLLECTION_NAME = 'visit'

_client = pymongo.MongoClient(MONGODB_URI)
_database = _client.get_database()


def store_action(user_id: str, action: str, data: str):
    collection = _database.get_collection(_COLLECTION_NAME)

    collection.insert_one({
        'viber_id': user_id,
        'action': action,
        'data': data,
        'date': datetime.datetime.now()
    })
