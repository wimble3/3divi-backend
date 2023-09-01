import json
import logging

import redis

import numpy as np

from settings import REDIS_HOST, REDIS_PORT, REDIS_DB


class RedisService:
    """Service for using redis."""
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        """Gets instance of redis-python class."""
        self.redis = redis.Redis(
            host=host, port=port, db=db, password="mypassword")

    def update(self, key, data):
        """
        Update by name of hash and key-value.
        Args:
            key (str): redis key
            data (dict): redis data

        Returns:
            None:

        """
        data_dump = json.dumps(data).encode("utf-8")
        return self.redis.set(key, data_dump)

    def get(self, key, list_to_np_array=True):
        """
        Get video data from redis by key.
        Args:
            key (str): redis key
            list_to_np_array (bool): if converting list to np array needed

        Returns:
            dict | None: data by key from radis or None

        """
        data = self.redis.get(key)

        if data:
            load = json.loads(data)
            if list_to_np_array:
                for i in load:
                    if isinstance(load[i], list):
                        load[i] = np.array(load[i])
            return load
        return None
