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

def check_for_alert(history, subscription):
    """Compare subscription to prices and create an alert if necessary. Returns None if no alert found."""

    alert = None

    if len(history):
        if lowest_spotprice(history, subscription['zone'].split()) > float(subscription['threshold']) and subscription['last_alert'] == 'Under':
            alert = {'subscription': subscription}
            alert['subscription']['last_alert'] = 'Over'
        elif lowest_spotprice(history, subscription['zone'].split()) <= float(subscription['threshold']) and subscription['last_alert'] == 'Over':
            alert = {'subscription': subscription}
            alert['subscription']['last_alert'] = 'Under'

    return alert
