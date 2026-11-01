
import base64
import json

from datetime import datetime
from src.database import get_connection


MAX_PAGE_SIZE = 100


def encode_cursor(timestamp, document_id):
    payload = {
        "timestamp": timestamp.isoformat(),
        "id": document_id,
    }

    serialized = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return base64.urlsafe_b64encode(serialized).decode("ascii")



def decode_cursor(cursor):
    if not isinstance(cursor, str) or not cursor:
        raise ValueError("El cursor debe ser una cadena no vacía.")

    try:
        decoded = base64.b64decode(
            cursor.encode("ascii"),
            altchars=b"-_",
            validate=True,
        )
        payload = json.loads(decoded.decode("utf-8"))
    except (ValueError, UnicodeError, TypeError):
        raise ValueError("El cursor no es válido.") from None

    if not isinstance(payload, dict):
        raise ValueError("El cursor no es válido.")

    if set(payload) != {"timestamp", "id"}:
        raise ValueError("La estructura del cursor no es válida.")

    if not isinstance(payload["timestamp"], str):
        raise ValueError("La fecha del cursor no es válida.")

    if isinstance(payload["id"], bool) or not isinstance(payload["id"], int):
        raise ValueError("El identificador del cursor no es válido.")

    if payload["id"] <= 0:
        raise ValueError("El identificador del cursor no es válido.")

    try:
        timestamp = datetime.fromisoformat(
            payload["timestamp"].replace("Z", "+00:00")
        )
    except ValueError:
        raise ValueError("La fecha del cursor no es válida.") from None

    if timestamp.tzinfo is None:
        raise ValueError("El cursor debe incluir zona horaria.")

    payload["timestamp"] = timestamp

    return payload


def validate_page_size(page_size):
    if (
        isinstance(page_size, bool)
        or not isinstance(page_size, int)
        or not 1 <= page_size <= MAX_PAGE_SIZE
    ):
        raise ValueError(
            f"page_size debe ser un entero entre 1 y {MAX_PAGE_SIZE}."
        )

    return page_size


def get_telemetry_page(device_id, page_size=20, cursor=None):
    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("device_id debe ser una cadena no vacía.")

    validate_page_size(page_size)

    cursor_data = decode_cursor(cursor) if cursor is not None else None

    with get_connection() as conn:
        with conn.cursor() as cur:
            if cursor_data is None:
                cur.execute(
                    """
                    SELECT id, device_id, timestamp, metric, value, unit
                    FROM telemetry_reading
                    WHERE device_id = %s
                    ORDER BY timestamp DESC, id DESC
                    LIMIT %s
                    """,
                    (device_id, page_size + 1),
                )
            else:
                cur.execute(
                    """
                    SELECT id, device_id, timestamp, metric, value, unit
                    FROM telemetry_reading
                    WHERE device_id = %s
                      AND (timestamp, id) < (%s, %s)
                    ORDER BY timestamp DESC, id DESC
                    LIMIT %s
                    """,
                    (
                        device_id,
                        cursor_data["timestamp"],
                        cursor_data["id"],
                        page_size + 1,
                    ),
                )

            rows = cur.fetchall()

    has_more = len(rows) > page_size
    items = rows[:page_size]

    next_cursor = None

    if has_more and items:
        last_item = items[-1]
        next_cursor = encode_cursor(last_item[2], last_item[0])

    return {
        "items": items,
        "next_cursor": next_cursor,
        "has_more": has_more,
    }
