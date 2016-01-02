#!/usr/bin/env python
"""
Identify price alerts.

"""

def lowest_spotprice(history, zones):
    """Return the lowest spotprice for the given zones or None if the history
    doesn't contain any prices for those zones. An empty zones list
    matches any zone."""
    price = None
    relevant_history = history

    if len(zones):
        relevant_history = filter (lambda x: x['AvailabilityZone'] in zones, history)

    if len(relevant_history) > 0:
        sorted_history = sorted(relevant_history, key=lambda x: x['SpotPrice'])
        price = float(sorted_history[0]['SpotPrice'])

    return price

def check_for_alerts(history, subscriptions):
    """Compare subscriptions to prices and create alerts."""
    alerts = []
    if len(history) and len(subscriptions):

        new_over = filter(
            lambda x: lowest_spotprice(history, x['zone'].split()) > float(x['threshold']) and x['last_alert'] == 'Under',
            subscriptions)

        new_under = filter(
            lambda x: lowest_spotprice(history, x['zone'].split()) <= float(x['threshold']) and x['last_alert'] == 'Over',
            subscriptions)

        subscriptions_with_alerts = new_over + new_under

        for sub in subscriptions_with_alerts:
            if sub['last_alert'] == 'Under':
                sub['last_alert'] = 'Over'
            elif sub['last_alert'] == 'Over':
                sub['last_alert'] = 'Under'
            alerts.append({'subscription':sub})

    return alerts
