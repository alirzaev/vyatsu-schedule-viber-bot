import motor.motor_asyncio as motor
from os import getenv

MONGODB_URI = getenv('MONGODB_URI')

_client = motor.AsyncIOMotorClient(MONGODB_URI)
_database = _client.get_database()


def get_database():
    return _database
