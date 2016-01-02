#!/usr/bin/env python
"""
Retrieves alert subscriptions from redis

"""

import redis

def get_subscriptions(redis_store):
    """ Pulls all of the subscriptions from the provided Redis store"""
    alarms = {}
    cursor = 0
    while True:
        cursor, keys = redis_store.scan(cursor, 'sb:alarm*')
        for key in keys:
            alarms[key] = redis_store.hgetall(key)
            alarms[key]['redis_key'] = key
        if cursor == 0:
            break
    return alarms
