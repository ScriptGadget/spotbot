#!/usr/bin/env python
"""
Test slack webhook messages.

"""

import unittest
from spotbot import slack

class SlackTest(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_format_notification(self):
        """ Test we can build a propely formatted message."""
        
        sub_virginia = {'name': 'My Virginia Spots',
               'threshold':'0.11',
               'region':'us-east-1',
               'zone': 'us-east-1d',
               'instance_type':'g2.2xlarge',
               'product':'Windows',
               'user':'1', 'last_alert':'Under'}

        alert_over = {'spot_price': 0.1200,
                 'last_alert': 'Over'}

        message = slack.format_notification(alert_over, sub_virginia)
        assert message == ":chart_with_upwards_trend: My Virginia Spots 15 minute low of 0.12 greater than 0.11"

        sub_virginia = {'name': 'My California Spots',
               'threshold':'0.22',
               'region':'us-east-1',
               'zone': 'us-east-1d',
               'instance_type':'g2.2xlarge',
               'product':'Windows',
               'user':'1', 'last_alert':'Over'}

        alert_over = {'spot_price': 0.0800,
                 'last_alert': 'Under'}
        
        message = slack.format_notification(alert_over, sub_virginia)
        assert message == ":chart_with_downwards_trend: My California Spots 15 minute low of 0.08 has returned below 0.22"



if __name__ == "__main__":
    unittest.main()
