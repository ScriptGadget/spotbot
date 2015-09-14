#!/usr/bin/env python
"""
Detect and send price alerts for AWS spot instances.

Retrieves alert subscriptions from redis and scans the requested clouds
firing-off any alerts discovered.

This script will normally be run by a cronjob.

"""

import datetime
import json
import boto3
import redis
import requests

def get_spot_prices(start_time, end_time, subscription):
    """ get spot prices. """
    client = boto3.client(
        service_name='ec2',
        region_name=subscription['region'],
    )

    return client.describe_spot_price_history(
        StartTime=start_time,
        EndTime=end_time,
        InstanceTypes=subscription['instance_types'].split(','),
        ProductDescriptions=subscription['products'].split(','),
        # AvailabilityZones=subscription['zones'].split(','),
    )['SpotPriceHistory']

def get_alert_subscriptions(redis_store):
    """ Pulls all alert subscriptions from Redis """
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

def check_alerts(redis_store, start, end, sub):
    """ Compare subscription to prices and identify alerts. """
    alert = None
    history = get_spot_prices(start, end, sub)
    if len(history) > 0:
        price = sorted(history, key=lambda x: x['SpotPrice'])[0]
        if sub.has_key('last_alert'):
            if sub['last_alert'] == 'Over':
                if float(price['SpotPrice']) < float(sub['threshold']):
                    redis_store.hset(sub['redis_key'], 'last_alert', 'Under')
                    price['alert'] = 'Under'
                    alert = price
            elif sub['last_alert'] == 'Under':
                if float(price['SpotPrice']) >= float(sub['threshold']):
                    redis_store.hset(sub['redis_key'], 'last_alert', 'Over')
                    price['alert'] = 'Over'
                    alert = price
        else:
            if float(price['SpotPrice']) < float(sub['threshold']):
                redis_store.hset(sub['redis_key'], 'last_alert', 'Under')
                price['alert'] = 'Under'
                alert = price
            elif float(price['SpotPrice']) >= float(sub['threshold']):
                redis_store.hset(sub['redis_key'], 'last_alert', 'Over')
                price['alert'] = 'Over'
                alert = price

    return alert

def send_alert_to_slack(web_hook,
                        channel="#alerts",
                        username="spotbot",
                        icon_emoji=":space_invader:",
                        message=":smile: Hello Slack!"):
    """ Send an alert message to a slack web hook. """
    data = {'channel' : channel,
            'username' : username,
            'text' : message,
            'icon_emoji' : icon_emoji}
    requests.post(web_hook, data=json.dumps(data))

def main():
    """ Make it all happen. """
    redis_store = redis.StrictRedis()

    now = datetime.datetime.utcnow()

    last_scan = redis_store.get('sb:last_scan')

    if last_scan is None:
        last_scan = now - datetime.timedelta(0, 15*60)

    subs = get_alert_subscriptions(redis_store)

    messages = {}
    for key in subs:
        sub = subs[key]
        alert = check_alerts(redis_store, last_scan, now, sub)
        if not alert is None:
            message = ":chart_with_upwards_trend: %s 15 minute low of %s greater than %s"
            message = message % (sub['name'], alert['SpotPrice'], sub['threshold'])

            if alert['alert'] == 'Under':
                message = ":chart_with_downwards_trend: "
                message += "%s 15 minute low of %s has returned below %s"
                message = message % (sub['name'], alert['SpotPrice'], sub['threshold'])

            if messages.has_key(sub['user']):
                messages[sub['user']] = messages[sub['user']] + "\n" + message

            else:
                messages[sub['user']] = message

    for user in messages:
        send_alert_to_slack(
            web_hook=redis_store.hget('sb:user#' + user, 'slack_webhook'),
            message=messages[user])

    redis_store.set('sb:last_scan', now)


main()
