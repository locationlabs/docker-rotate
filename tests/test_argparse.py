from datetime import timedelta

from dockerrotate.main import parse_arguments


def test_timestamp_parsing():

    assert parse_arguments(['containers', '--created', '1h']).created == timedelta(hours=1)
    assert parse_arguments(['containers', '--created', '23m']).created == timedelta(minutes=23)
    assert parse_arguments(['containers', '--created', '2d']).created == timedelta(days=2)
    assert parse_arguments(['containers', '--created', '0h']).created == timedelta()
    assert parse_arguments(['containers', '--created', '0']).created == timedelta()
