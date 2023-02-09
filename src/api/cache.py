from abc import ABC
import redis
import logging

FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Cache(ABC):
    def __init__(self):
        pass

    def add_value(self, key: str, value: float):
        pass

    def get_value(self, key:str):
        pass

class RedisCache(Cache):
    def __init__(self):
        self.storage = redis.Redis(host='127.0.0.1', port=6379, db=0)
        super().__init__()

    def add_value(self, key: str, value):
        logger.debug(f'add value [{key}, {value}] into cache')
        self.storage.set(key, value)

    def get_value(self, key:str):
        result = self.storage.get(key)
        logger.debug(f'get value from {key} is {result}')
        return result



def get_ticket_key(orig: str, dest: str, date: str):
    date = ''.join(date.split('-')[:2])
    return orig + '-' + dest + '-' + date
