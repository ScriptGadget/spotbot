#!/usr/bin/env python
"""
Send notifications to Slack.

"""
import json
import requests

def format_notification(alert, sub):
    message = None

    if alert['last_alert'] == 'Over':
        message = ":chart_with_upwards_trend: "
        message += "%s 15 minute low of %s greater than %s"
        message = message % (sub['name'],
                             alert['spot_price'],
                             sub['threshold'])

    elif alert['last_alert'] == 'Under':
        message = ":chart_with_downwards_trend: "
        message += "%s 15 minute low of %s has returned below %s"
        message = message % (sub['name'],
                             alert['spot_price'],
                             sub['threshold'])

    return message

def send_notification(web_hook, channel="#alerts",
                      username="spotbot", icon_emoji=":space_invader:",
                      message=":smile: Hello Slack!"):
    """Send an alert message to a slack web hook. This is just a very
    thin wrapper around requests.post and returns the result of that
    call."""


    requests.post(web_hook, data=json.dumps({'channel' : channel,
                                             'username' : username,
                                             'text' : message,
                                             'icon_emoji' : icon_emoji}))

