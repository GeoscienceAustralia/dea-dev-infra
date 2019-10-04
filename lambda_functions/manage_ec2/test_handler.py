from lambda_functions.manage_ec2.handler import handler, _time_in_range, _schedule_start_stop_instances
from unittest import TestCase, mock
from datetime import datetime
from moto import mock_ec2
import boto3
import os

class TestLambda(TestCase):
    schedule_tag = 'stopAtNight'
    schedule_start_time = "07:00"
    schedule_stop_time = "18:00"
    time_zone = 'Australia/Sydney'

    start_time = datetime.strptime(schedule_start_time, '%H:%M').time()
    stop_time = datetime.strptime(schedule_stop_time, '%H:%M').time()

    def setUp(self):
        os.environ['SCHEDULE_TAG'] = self.schedule_tag
        os.environ['SCHEDULE_START_TIME'] = self.schedule_start_time
        os.environ['SCHEDULE_STOP_TIME'] = self.schedule_stop_time
        os.environ['TIME_ZONE'] = self.time_zone

    def test_lambda_handler(self):
        event = {}
        with mock.patch('lambda_functions.manage_ec2.handler._schedule_start_stop_instances') as mock_schedule_start_stop_instances:
            handler(event, None)
            mock_schedule_start_stop_instances.assert_called_once()

    @mock_ec2
    def test_schedule_start_stop_instances_start_instances_when_current_time_in_time_range(self):
        ec2 = boto3.client('ec2', region_name='ap-southeast-2')
        ec2.run_instances(
            ImageId='ami-1234abcd',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'stopAtNight',
                            'Value': 'true',
                        },
                    ],
                }
            ],
        )
        current_time = datetime.strptime("10:00", '%H:%M').time()

        result = _schedule_start_stop_instances(self.schedule_tag, self.start_time, self.stop_time, current_time)

        assert result == 'starting'

    @mock_ec2
    def test_schedule_start_stop_instances_stop_instances_when_current_time_outside_time_range(self):
        ec2 = boto3.client('ec2', region_name='ap-southeast-2')
        ec2.run_instances(
            ImageId='ami-1234abcd',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'stopAtNight',
                            'Value': 'true',
                        },
                    ],
                },
            ],
        )
        current_time = datetime.strptime("18:00", '%H:%M').time()

        result = _schedule_start_stop_instances(self.schedule_tag, self.start_time, self.stop_time, current_time)

        assert result == 'starting'

    def test_time_in_range_return_true_if_current_time_in_range(self):
        current_time = datetime.strptime("07:00", '%H:%M').time()

        result = _time_in_range(self.start_time, self.stop_time, current_time)

        assert result == True

    def test_time_in_range_return_false_if_current_time_out_of_range(self):
        current_time = datetime.strptime("19:00", '%H:%M').time()

        result = _time_in_range(self.start_time, self.stop_time, current_time)

        assert result == False
