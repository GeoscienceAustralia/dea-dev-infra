from .handler import _time_in_range
import unittest
from datetime import datetime

def test_time_in_range_return_true_if_current_time_in_range():
    start_time = datetime.strptime("07:00", '%H:%M').time()
    stop_time = datetime.strptime("18:00", '%H:%M').time()
    current_time = datetime.strptime("07:00", '%H:%M').time()

    result = _time_in_range(start_time, stop_time, current_time)

    assert result == True

def test_time_in_range_return_false_if_current_time_out_of_range():
    start_time = datetime.strptime("07:00", '%H:%M').time()
    stop_time = datetime.strptime("18:00", '%H:%M').time()
    current_time = datetime.strptime("19:00", '%H:%M').time()

    result = _time_in_range(start_time, stop_time, current_time)

    assert result == False




