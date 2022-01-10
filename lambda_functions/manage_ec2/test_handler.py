from handler import handler, _time_in_range, _schedule_start_stop_instances
from unittest import TestCase, mock
from unittest.mock import ANY
from datetime import datetime
from moto import mock_ec2
import boto3
import os

class TestLambda(TestCase):
    schedule_tag = 'myTestTag'
    schedule_start_time = "08:00"
    schedule_stop_time = "17:00"
    time_zone = 'Australia/Sydney'
    christmas_shutdown_startday = '25/12/2021'
    christmas_shutdown_lastday = '04/01/2022'

    start_time = datetime.strptime(schedule_start_time, '%H:%M').time()
    stop_time = datetime.strptime(schedule_stop_time, '%H:%M').time()

    def setUp(self):
        os.environ['SCHEDULE_TAG'] = self.schedule_tag
        os.environ['SCHEDULE_START_TIME'] = self.schedule_start_time
        os.environ['SCHEDULE_STOP_TIME'] = self.schedule_stop_time
        os.environ['TIME_ZONE'] = self.time_zone

    def test_lambda_handler(self):
        event = {}
        with mock.patch('handler._schedule_start_stop_instances') as mock_schedule_start_stop_instances:
            handler(event, None)
            mock_schedule_start_stop_instances.assert_called_with(self.schedule_tag, self.start_time, self.stop_time, ANY)

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
                            'Key': self.schedule_tag,
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
                            'Key': self.schedule_tag,
                            'Value': 'true',
                        },
                    ],
                },
            ],
        )
        current_time = datetime.strptime("22:00", '%H:%M').time()

        result = _schedule_start_stop_instances(self.schedule_tag, self.start_time, self.stop_time, current_time)

        assert result == 'stopping'

    def test_time_in_range_return_true_if_current_time_in_range(self):
        current_time = datetime.strptime("10:00", '%H:%M').time()

        result = _time_in_range(self.start_time, self.stop_time, current_time)

        assert result == True

    def test_time_in_range_return_false_if_current_time_out_of_range(self):
        current_time = datetime.strptime("19:00", '%H:%M').time()

        result = _time_in_range(self.start_time, self.stop_time, current_time)

        assert result == False

    def test_date_in_range_return_true_if_selected_date_in_christmas_shutdown_range(self):
        selected_date = datetime.strptime('4/1/2022', '%d/%m/%Y')

        result = _time_in_range(
            datetime.strptime(self.christmas_shutdown_startday, "%d/%m/%Y"),
            datetime.strptime(self.christmas_shutdown_lastday, "%d/%m/%Y"),
            selected_date
        )

        assert result == True

    def test_date_in_range_return_false_if_selected_date_out_of_christmas_shutdown_range(self):
        selected_date = datetime.strptime('5/1/2022', '%d/%m/%Y')

        result = _time_in_range(
            datetime.strptime(self.christmas_shutdown_startday, "%d/%m/%Y"),
            datetime.strptime(self.christmas_shutdown_lastday, "%d/%m/%Y"),
            selected_date
        )

        assert result == False