#!/usr/bin/env python
"""
Send price alerts.

"""

def check_for_alerts(history, subscriptions):
    """Compare subscriptions to prices and create alerts."""
    alerts = []
    if len(history) and len(subscriptions):
        price = sorted(history, key=lambda x: x['SpotPrice'])[0]['SpotPrice']

        new_over = filter(
            lambda x: float(price) > float(x['threshold']) and x['last_alert'] == 'Under',
            subscriptions)

        new_under = filter(
            lambda x: float(price) <= float(x['threshold']) and x['last_alert'] == 'Over',
            subscriptions)

        alerts = new_over + new_under
    return alerts
