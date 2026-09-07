```python
from datetime import datetime
from decimal import Decimal, InvalidOperation


MIN_TEMPERATURE = Decimal("-50.00")
MAX_TEMPERATURE = Decimal("100.00")

ALLOWED_METRIC = "temperature"
ALLOWED_UNIT = "°C"


def validate_telemetry(reading):
    """
    Valida una lectura de telemetría según el contrato M01.

    Retorna:
        (True, []) cuando la lectura es válida.
        (False, errores) cuando la lectura no cumple el contrato.
    """

    errors = []

    # Campos definidos por el contrato y la tabla PostgreSQL.
    required_fields = [
        "device_id",
        "timestamp",
        "metric",
        "value",
        "unit",
    ]

    # 1. Verificar campos obligatorios
    for field in required_fields:
        if field not in reading or reading[field] is None:
            errors.append(f"{field} is required")

    # Si falta algún campo, no continuamos con las validaciones
    # que dependen de ese campo.
    if errors:
        return False, errors

    # 2. Validar device_id
    if not isinstance(reading["device_id"], str):
        errors.append("device_id must be a string")
    elif reading["device_id"].strip() == "":
        errors.append("device_id cannot be empty")

    # 3. Validar timestamp
    if not isinstance(reading["timestamp"], str):
        errors.append("timestamp must be an ISO 8601 string")
    else:
        try:
            datetime.fromisoformat(
                reading["timestamp"].replace("Z", "+00:00")
            )
        except ValueError:
            errors.append("timestamp must have ISO 8601 format")

    # 4. Validar metric
    if reading["metric"] != ALLOWED_METRIC:
        errors.append("metric must be temperature")

    # 5. Validar value
    try:
        value = Decimal(str(reading["value"]))

        if value < MIN_TEMPERATURE:
            errors.append("value must be greater than or equal to -50.00")

        elif value > MAX_TEMPERATURE:
            errors.append("value must be less than or equal to 100.00")

    except (InvalidOperation, ValueError, TypeError):
        errors.append("value must be a decimal number")

    # 6. Validar unit
    if reading["unit"] != ALLOWED_UNIT:
        errors.append("unit must be °C")

    return len(errors) == 0, errors


# -------------------------------------------------------------------
# Casos definidos en el contrato M01
# -------------------------------------------------------------------

NORMAL_CASE = {
    "device_id": "sensor-001",
    "timestamp": "2026-09-06T10:30:00Z",
    "metric": "temperature",
    "value": 23.50,
    "unit": "°C",
}

LOWER_BOUNDARY_CASE = {
    "device_id": "sensor-001",
    "timestamp": "2026-09-06T10:31:00Z",
    "metric": "temperature",
    "value": -50.00,
    "unit": "°C",
}

UPPER_BOUNDARY_CASE = {
    "device_id": "sensor-001",
    "timestamp": "2026-09-06T10:32:00Z",
    "metric": "temperature",
    "value": 100.00,
    "unit": "°C",
}

DECLARED_FAILURE_CASE = {
    "device_id": "sensor-001",
    "timestamp": "2026-09-06T10:33:00Z",
    "metric": "temperature",
    "value": 150.00,
    "unit": "°C",
}
```

