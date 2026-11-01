
import pytest

from src.document_pagination import (
    encode_cursor,
    decode_cursor,
    validate_page_size,
)


def test_cursor_round_trip():
    cursor = encode_cursor("sensor-01", "doc-001")

    assert decode_cursor(cursor, "sensor-01") == "doc-001"


def test_cursor_rejects_another_device():
    cursor = encode_cursor("sensor-01", "doc-001")

    with pytest.raises(ValueError, match="otro dispositivo"):
        decode_cursor(cursor, "sensor-02")


def test_cursor_rejects_invalid_content():
    with pytest.raises(ValueError, match="no es válido"):
        decode_cursor("cursor-invalido", "sensor-01")


def test_cursor_rejects_empty_value():
    with pytest.raises(ValueError, match="no vacía"):
        decode_cursor("", "sensor-01")


def test_page_size_accepts_normal_value():
    assert validate_page_size(20) == 20


def test_page_size_accepts_upper_boundary():
    assert validate_page_size(100) == 100


@pytest.mark.parametrize("value", [0, -1, 101, 1.5, True, "10", None])
def test_page_size_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        validate_page_size(value)
