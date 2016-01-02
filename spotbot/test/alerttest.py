#!/usr/bin/env python
"""
Detect and send price alerts for AWS spot instances.

Retrieves alert subscriptions from redis and scans the requested clouds
firing-off any alerts discovered.

This script will normally be run by a cronjob.

"""

import unittest
import datetime
from dateutil.tz import tzutc
from spotbot import alert

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    """ Borrow isclose from Python 3.5 """
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class AlertTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_check_for_alerts_empty_history_and_subscriptions(self):
        """ Test that we handle no history and no subscriptions in a sane way."""
        assert alert.check_for_alerts([],[]) == [], "Alerts should have been an empty list."

    def test_check_for_alerts_over_under(self):
        """ Test that we can match an alert description against relevant history. """

        history = [ {u'Timestamp': datetime.datetime(2015, 12, 31, 22, 13, 43,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.105200',
                     u'AvailabilityZone': 'us-east-1b'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 56, 18,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.104400',
                     u'AvailabilityZone': 'us-east-1d'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 56, 18,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.106300',
                     u'AvailabilityZone': 'us-east-1c'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 31, 6,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.767100',
                     u'AvailabilityZone': 'us-east-1e'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 29, 47,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.105300',
                     u'AvailabilityZone': 'us-east-1b'},
        ]

        subscriptions = [
            {'name': 'Dublin Under Twenty',
             'threshold':'0.2',
             'region':'eu-west-1',
             'zone': 'eu-west-1b',
             'instance_type':'g2.2xlarge',
             'product':'Windows',
             'user':'1',
             'last_alert':'Under'},
            {'name': 'Virginia Over Twenty',
             'threshold':'0.2',
             'region':'us-east-1',
             'zone': 'us-east-1b',
             'instance_type':'g2.2xlarge',
             'product':'Windows',
             'user':'1',
             'last_alert':'Over'},
            {'name': 'Virginia Under Twenty',
             'threshold':'0.2',
             'region':'us-east-1',
             'zone': 'us-east-1b',
             'instance_type':'g2.2xlarge',
             'product':'Windows',
             'user':'1',
             'last_alert':'Under'},
            {'name': 'Virginia Under A Nickle',
             'threshold':'0.05',
             'region':'us-east-1',
             'zone': 'us-east-1b',
             'instance_type':'g2.2xlarge',
             'product':'Windows',
             'user':'1',
             'last_alert':'Under'},
        ]


        alerts = alert.check_for_alerts(history, subscriptions)
        alert_names = ['Virginia Under A Nickle', 'Virginia Over Twenty']
        assert len(filter(lambda x: x['subscription']['name'] in alert_names, alerts)) == len(alert_names), "I didn't find one of %s in %s." % (alert_names, alerts)



    def test_check_for_alerts_with_no_matched_zones(self):
        """Alerts are only valid if the availability zone in the history matches an availability zone in the subscription"""

        history = [{u'Timestamp': datetime.datetime(2015, 12, 31, 22, 13, 43,
                                                    tzinfo=tzutc()),
                    u'ProductDescription': 'Windows',
                    u'InstanceType': 'g2.2xlarge',
                    u'SpotPrice': '0.105200',
                    u'AvailabilityZone': 'us-east-1d'},
                   {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 56, 18,
                                                    tzinfo=tzutc()),
                    u'ProductDescription': 'Windows',
                    u'InstanceType': 'g2.2xlarge',
                    u'SpotPrice': '0.104400',
                    u'AvailabilityZone': 'us-east-1d'}]

        all_except_1d = [{'name': 'All except 1d',
                          'threshold':'0.05',
                          'region':'us-east-1',
                          'zone': 'us-east-1a,us-east-1b,us-east-1c',
                          'instance_type':'g2.2xlarge',
                          'product':'Windows',
                          'user':'1',
                          'last_alert':'Under'}]

        alerts = alert.check_for_alerts(history, all_except_1d)
        assert len(alerts) == 0, 'There should not be an alert for "%s"' % (all_except_1d[0]['subscription']['name'])


    def test_check_for_alerts_match_zone(self):
        """When we match a zone and all other criteria, we should create an alert."""

        history = [{u'Timestamp': datetime.datetime(2015, 12, 31, 22, 13, 43,
                                                    tzinfo=tzutc()),
                    u'ProductDescription': 'Windows',
                    u'InstanceType': 'g2.2xlarge',
                    u'SpotPrice': '0.105200',
                    u'AvailabilityZone': 'us-east-1d'},
                   {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 56, 18,
                                                    tzinfo=tzutc()),
                    u'ProductDescription': 'Windows',
                    u'InstanceType': 'g2.2xlarge',
                    u'SpotPrice': '0.104400',
                    u'AvailabilityZone': 'us-east-1d'}]

        match_1d = [{'name': 'Sub for just 1d',
                     'threshold':'0.05',
                     'region':'us-east-1',
                     'zone': 'us-east-1d',
                     'instance_type':'g2.2xlarge',
                     'product':'Windows',
                     'user':'1',
                     'last_alert':'Under'}]

        alerts = alert.check_for_alerts(history, match_1d)
        alert_names = [match_1d[0]['name']]
        assert len(filter(lambda x: x['subscription']['name'] in alert_names, alerts)) == len(alert_names), "There should be an alert for %s in %s." % (alert_names, alerts)

        match_1q = [{'name': 'Sub for 1q',
                     'threshold':'0.05',
                     'region':'us-east-1',
                     'zone': 'us-east-1q',
                     'instance_type':'g2.2xlarge',
                     'product':'Windows',
                     'user':'1',
                     'last_alert':'Under'}]

        assert len(alert.check_for_alerts(history, match_1q)) == 0, "There should not be any alerts for us_east-1q"

    def test_check_for_alerts_sets_last_alert(self):
        """check_for_alerts should set the last_alert attribute of the alert to indication the type of the alert."""

        history = [ {u'Timestamp': datetime.datetime(2015, 12, 31, 22, 13, 43,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.105200',
                     u'AvailabilityZone': 'us-east-1b'}]
        subscriptions = [{'name': 'Sub for 1b',
                     'threshold':'0.05',
                     'region':'us-east-1',
                     'zone': 'us-east-1b',
                     'instance_type':'g2.2xlarge',
                     'product':'Windows',
                     'user':'1',
                     'last_alert':'Under'}]
        alerts = alert.check_for_alerts(history, subscriptions)
        assert len(alerts) == 1, "There should be an alert for us_east-1b"
        assert alerts[0]['subscription']['last_alert'] == 'Over'

    def test_lowest_spotprice(self):
        """We should find the lowest spotprice for a given zone or return None."""

        history = [ {u'Timestamp': datetime.datetime(2015, 12, 31, 22, 13, 43,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.105200',
                     u'AvailabilityZone': 'us-east-1b'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 56, 18,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.104400',
                     u'AvailabilityZone': 'us-east-1d'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 56, 18,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.106300',
                     u'AvailabilityZone': 'us-east-1c'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 31, 6,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.767100',
                     u'AvailabilityZone': 'us-east-1e'},
                    {u'Timestamp': datetime.datetime(2015, 12, 31, 21, 29, 47,
                                                     tzinfo=tzutc()),
                     u'ProductDescription': 'Windows',
                     u'InstanceType': 'g2.2xlarge',
                     u'SpotPrice': '0.105300',
                     u'AvailabilityZone': 'us-east-1b'},
        ]

        price = alert.lowest_spotprice(history, ['us-east-1q','us-east-1b'])
        assert not price is None, "A price should have been returned for us-east-1b"
        assert isclose(price, 0.105200), "should have found the lower price for us-east-1b only."

        price = alert.lowest_spotprice(history, [])
        assert not price is None, "A price should have been returned for the empty zone list."
        assert isclose(alert.lowest_spotprice(history, []), 0.104400), "An empty zone list should match any zone."


if __name__ == "__main__":
    unittest.main()
