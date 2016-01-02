#!/usr/bin/env python
"""
Gather spot price information from AWS.
"""

import boto3

def get_spot_history_from_aws(start_time, end_time, subscription):
    """Returns spot price history for the period between the timestamps if
    those price history events match the subscription

    start_time and end_time should be in UTC.

    subscription should be in the form:
    subscriptions = {'name': 'MyAlert For Dublin G2',
             'threshold':'0.2',
             'region':'eu-west-1',
             'zone': 'eu-west-1b',
             'instance_type':'g2.2xlarge',
             'product':'Windows',
             'user':'1',
             'last_alert':'Under'}


    This is just a very thin wrapper around a call to the boto3 AWS
    client. We only support subscriptions to a single product,
    instance_type and zone. For now, we just return the same
    represenation of SpotPriceHistory that boto3 returns which in-turn, follows the AWS JSON response, and this is
    what the alert module will expect from us. e.g.:

    history = [{u'Timestamp': datetime.datetime(2015, 12, 31, 22, 13, 43,
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
    u'AvailabilityZone': 'us-east-1d'}]

    """
    client = boto3.client(
        service_name='ec2',
        region_name=subscription['region'],
    )

    return client.describe_spot_price_history(
        StartTime=start_time,
        EndTime=end_time,
        InstanceTypes=subscription['instance_type'].split(','),
        ProductDescriptions=subscription['product'].split(','),
        AvailabilityZones=subscription['zone'].split(','),
    )['SpotPriceHistory']

