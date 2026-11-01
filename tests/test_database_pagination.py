import pytest
from datetime import datetime, timezone

from src.database_pagination import (
    encode_cursor,
    decode_cursor,
    validate_page_size,
)


def test_cursor_round_trip():
    timestamp = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)

    cursor = encode_cursor(timestamp, 10)
    decoded = decode_cursor(cursor)

    assert decoded["id"] == 10
    assert decoded["timestamp"] == timestamp


def test_cursor_rejects_empty_value():
    with pytest.raises(ValueError):
        decode_cursor("")


def test_cursor_rejects_invalid_content():
    with pytest.raises(ValueError):
        decode_cursor("esto-no-es-un-cursor")


@pytest.mark.parametrize("page_size", [1, 20, 100])
def test_valid_page_sizes(page_size):
    assert validate_page_size(page_size) == page_size


@pytest.mark.parametrize(
    "page_size",
    [0, -1, 101, 1.5, True, "10", None],
)
def test_invalid_page_sizes(page_size):
    with pytest.raises(ValueError):
        validate_page_size(page_size)