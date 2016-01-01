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



class AlertTest(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def testcheck_for_alerts_empty_history_and_subscriptions(self):
        """ Test that we handle no history and no subscriptions in a sane way."""
        assert alert.check_for_alerts([],[]) == [], "Alerts should have been an empty list."


    def testcheck_for_alerts(self):
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
             'zones': 'eu-west-1a,eu-west-1b,eu-west-1c',
             'instance_types':'g2.2xlarge',
             'products':'Windows',
             'user':'1',
             'last_alert':'Under'},
            {'name': 'Virginia Over Twenty',
             'threshold':'0.2',
             'region':'us-east-1',
             'zones': 'us-east-1a,us-east-1b,us-east-1c',
             'instance_types':'g2.2xlarge',
             'products':'Windows',
             'user':'1',
             'last_alert':'Over'},
            {'name': 'Virginia Under Twenty',
             'threshold':'0.2',
             'region':'us-east-1',
             'zones': 'us-east-1a,us-east-1b,us-east-1c',
             'instance_types':'g2.2xlarge',
             'products':'Windows',
             'user':'1',
             'last_alert':'Under'},
            {'name': 'Virginia Under A Nickle',
             'threshold':'0.05',
             'region':'us-east-1',
             'zones': 'us-east-1a,us-east-1b,us-east-1c',
             'instance_types':'g2.2xlarge',
             'products':'Windows',
             'user':'1',
             'last_alert':'Under'},
        ]


        alerts = alert.check_for_alerts(history, subscriptions)

        alert_names = ['Virginia Under A Nickle', 'Virginia Over Twenty']

        assert len(filter(lambda x: x['name'] in alert_names, alerts)) == len(alert_names), "I didn't find one of %s in %s." % (alert_names, alerts)


if __name__ == "__main__":
    unittest.main()
