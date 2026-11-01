
import base64
import json


MAX_PAGE_SIZE = 100


def encode_cursor(device_id, document_id):
    """Genera un cursor opaco para continuar una consulta."""
    payload = {
        "device_id": device_id,
        "document_id": document_id,
    }

    serialized = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return base64.urlsafe_b64encode(serialized).decode("ascii")


def decode_cursor(cursor, expected_device_id):
    """Valida y decodifica un cursor de paginación."""
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

    if set(payload) != {"device_id", "document_id"}:
        raise ValueError("La estructura del cursor no es válida.")

    if payload["device_id"] != expected_device_id:
        raise ValueError("El cursor pertenece a otro dispositivo.")

    document_id = payload["document_id"]

    if not isinstance(document_id, str) or not document_id.strip():
        raise ValueError("El identificador del cursor no es válido.")

    return document_id


def validate_page_size(page_size):
    """Valida el tamaño solicitado para una página."""
    if isinstance(page_size, bool) or not isinstance(page_size, int):
        raise ValueError("page_size debe ser un número entero.")

    if not 1 <= page_size <= MAX_PAGE_SIZE:
        raise ValueError(
            f"page_size debe estar entre 1 y {MAX_PAGE_SIZE}."
        )

    return page_size