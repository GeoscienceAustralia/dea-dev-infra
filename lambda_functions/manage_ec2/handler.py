import json
import logging
import os
from datetime import datetime
from dateutil.tz import tz
import boto3
from botocore.exceptions import ClientError

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

REGION = 'ap-southeast-2'
TIME_ZONE = tz.gettz(os.environ.get('TIME_ZONE'))


def _time_in_range(start, end, x):
    """
    Returns true if x is in the time range (start, end)
    Where start, end, x are datetime objects
    """
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def handler(event, context):
    """
    This function finds instances tagged with SCHEDULE_TAG.
    It will then power on / off each instance based on SCHEDULE_START_TIME and SCHEDULE_STOP_TIME provided.
    """

    LOG.info("Received event: %s", json.dumps(event, indent=2))

    ec2 = boto3.client('ec2', region_name=REGION)

    now = datetime.now(tz=TIME_ZONE).time()
    LOG.info('Current time is %s', now)

    start_time = os.environ.get('SCHEDULE_START_TIME')
    start_time = datetime.strptime(start_time, '%H:%M').time()
    stop_time = os.environ.get('SCHEDULE_STOP_TIME')
    stop_time = datetime.strptime(stop_time, '%H:%M').time()
    LOG.info("Start Time: %s, Stop Time: %s", start_time, stop_time)

    instances = [
        {
            'Name': 'tag:' + os.environ.get('SCHEDULE_TAG'),
            'Values': ['true']
        },
    ]

    instance_ids = []
    ec2_reservations = ec2.describe_instances(Filters=instances)['Reservations']

    for reservation in ec2_reservations:
        ec2_instances = reservation['Instances']
        for instance in ec2_instances:
            instance_ids.append(instance['InstanceId'])

    if _time_in_range(start_time, stop_time, now):
        LOG.info("Starting instance: %s", (','.join(instance_ids)))
        try:
            ec2.start_instances(InstanceIds=instance_ids)
        except ClientError as e:
            LOG.error(e)
    else:
        LOG.info("Stopping instance: %s", (','.join(instance_ids)))
        try:
            ec2.stop_instances(InstanceIds=instance_ids)
        except ClientError as e:
            LOG.error(e)