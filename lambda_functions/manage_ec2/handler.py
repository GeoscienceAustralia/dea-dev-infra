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


def _schedule_start_stop_instances(schedule_tag, start_time, stop_time, now):
    ec2 = boto3.client('ec2', region_name=REGION)

    instances = [
        {
            'Name': 'tag:' + schedule_tag,
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
            return 'starting'
        except ClientError as e:
            LOG.error(e)
    else:
        LOG.info("Stopping instance: %s", (','.join(instance_ids)))
        try:
            ec2.stop_instances(InstanceIds=instance_ids)
            return 'stopping'
        except ClientError as e:
            LOG.error(e)


def handler(event, context):
    """
    This function finds instances tagged with SCHEDULE_TAG.
    It will then power on / off each instance based on SCHEDULE_START_TIME and SCHEDULE_STOP_TIME provided.
    """

    LOG.info("Received event: %s", json.dumps(event, indent=2))

    now = datetime.now(tz=TIME_ZONE).time()
    start_time = datetime.strptime(os.getenv('SCHEDULE_START_TIME'), '%H:%M').time()
    stop_time = datetime.strptime(os.getenv('SCHEDULE_STOP_TIME'), '%H:%M').time()
    LOG.info("Current time: %s, Start Time: %s, Stop Time: %s", now, start_time, stop_time)

    schedule_tag = os.getenv('SCHEDULE_TAG')

    _schedule_start_stop_instances(schedule_tag, start_time, stop_time, now)
