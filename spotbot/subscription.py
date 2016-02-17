#!/usr/bin/env python
"""
Manage the subscriptions using a shelf

"""

import shelve

def get_subscriptions(state_store):
    """ Pulls all of the subscriptions from the provided store"""
    return state_store['subscriptions']

def get_state_store():
    return shelve.open('spotbot-shelf', writeback=True);

def get_last_scan(state_store):
    return state_store['last_scan'] if state_store.has_key('last_scan') else None 

def set_last_scan(state_store, last_scan):
    state_store['last_scan'] = last_scan

def get_web_hook(state_store, user):
    return state_store['users'][user]['slack_webhook']

def get_notification_channel(state_store, user):
    return state_store['users'][user]['slack_channel']

def update_subscription_with_last_result(state_store, key, alert):
    subscriptions = get_subscriptions(state_store)
    subscription = subscriptions[key]
    subscription['last_alert'] = alert['last_alert']
    subscriptions['key'] = subscription
    state_store['subscriptions'] = subscriptions

def close_state_store(state_store):
    state_store.sync()
    state_store.close()
