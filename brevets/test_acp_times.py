"""
Nose tests for acp_times.py.
Expected values checked against https://rusa.org/octime_acp.html
"""
import acp_times
from nose.tools import assert_raises


START = "2026-01-01T00:00:00+00:00"   # midnight, so the expected time = the duration


def test_open_uses_segments():
    assert acp_times.open_time(350, 400, START) == "2026-01-01T10:34:00+00:00"

def test_close_within_first_60km():
    assert acp_times.close_time(20, 200, START) == "2026-01-01T02:00:00+00:00"

def test_open_rounds_to_nearest_minute():
    assert acp_times.open_time(60, 200, START) == "2026-01-01T01:46:00+00:00"

def test_close_from_finish():
    assert acp_times.close_time(200, 200, START) == "2026-01-01T13:30:00+00:00"

def test_close_overshoot_uses_brevet_distance():
    assert acp_times.close_time(205, 200, START) == "2026-01-01T13:30:00+00:00"

def test_close_past_600():
    assert acp_times.close_time(890, 1000, START) == "2026-01-03T17:23:00+00:00"

def test_close_after_1hr():
    assert acp_times.close_time(0, 200, START) == "2026-01-01T01:00:00+00:00"

def test_open_at_start():
    assert acp_times.open_time(0, 200, START) == "2026-01-01T00:00:00+00:00"

def test_too_far_past_finish_is_rejected():
    assert_raises(ValueError, acp_times.open_time, 300, 200, START)
