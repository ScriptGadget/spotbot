#!/usr/bin/env python
"""
Retrieves alert subscriptions from redis

"""

import redis

def get_subscriptions(state_store):
    """ Pulls all of the subscriptions from the provided Redis store"""
    alarms = {}
    cursor = 0
    while True:
        cursor, keys = state_store.scan(cursor, 'sb:alarm*')
        for key in keys:
            alarms[key] = state_store.hgetall(key)
            alarms[key]['redis_key'] = key
        if cursor == 0:
            break
    return alarms

def get_state_store():
    return redis.StrictRedis()

def get_last_scan(state_store):
    return state_store.get('sb:last_scan')

def set_last_scan(state_store, last_scan):
    state_store.set('sb:last_scan', last_scan)

def get_web_hook(state_store, user):
    return state_store.hget('sb:user#' + user, 'slack_webhook')

def get_notification_channel(state_store, user):
    return state_store.hget('sb:user#' + user, 'slack_channel')
