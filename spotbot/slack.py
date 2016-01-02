#!/usr/bin/env python
"""
Send notifications to Slack.

"""
import json
import requests

def send_notification(web_hook, channel="#alerts", username="spotbot",
                      icon_emoji=":space_invader:", message=":smile:
                      Hello Slack!"):
    """Send an alert message to a slack web hook. This is just a very
    thin wrapper around requests.post and returns the result of that
    call."""


    requests.post(web_hook, data=json.dumps({'channel' : channel,
                                             'username' : username,
                                             'text' : message,
                                             'icon_emoji' : icon_emoji}))

