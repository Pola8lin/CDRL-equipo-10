import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.document_store import DocumentStore
from src.validator import validate_telemetry


def make_reading(value):
    """Genera un diccionario de telemetría base para usar en las pruebas."""
    return {
        "device_id": "sensor-m05-test",
        "timestamp": "2026-10-01T10:30:00Z",
        "metric": "temperature",
        "value": value,
        "unit": "°C",
    }


def make_store():
    """Instancia la conexión a Firestore para las pruebas."""
    return DocumentStore()


def test_m05_normal_document_is_valid():
    # Valida que un documento con datos correctos dentro del rango sea aceptado
    valid, errors = validate_telemetry(make_reading(23.50))
    assert valid is True
    assert errors == []


def test_m05_lower_boundary_is_valid():
    # Verifica que el límite inferior permitido para la temperatura sea válido
    valid, errors = validate_telemetry(make_reading(-50.00))
    assert valid is True
    assert errors == []


def test_m05_upper_boundary_is_valid():
    # Verifica que el límite superior permitido para la temperatura sea válido
    valid, errors = validate_telemetry(make_reading(100.00))
    assert valid is True
    assert errors == []


def test_m05_declared_failure_is_rejected():
    # Confirma que los valores fuera del rango permitido sean rechazados
    valid, errors = validate_telemetry(make_reading(150.00))
    assert valid is False
    assert errors != []


def test_m05_create_document():
    store = make_store()
    reading = make_reading(23.50)
    
    # Crea el documento y verifica que el ID retornado sea correcto
    result = store.create_document("m05-test-001", reading)
    assert result == "m05-test-001"
    
    # Confirma que el documento se haya guardado correctamente en la base de datos
    saved = store.get_document("m05-test-001")
    assert saved == reading


def test_m05_get_existing_document():
    store = make_store()
    reading = make_reading(24.00)
    
    # Inserta un documento de prueba para posteriormente realizar la consulta
    store.create_document("m05-test-002", reading) 
    
    # Valida que la lectura recupere exactamente los datos guardados
    result = store.get_document("m05-test-002")
    assert result == reading


def test_m05_get_absent_document():
    store = make_store()
    # Verifica el manejo de errores al consultar un identificador que no existe
    result = store.get_document("m05-no-existe-nunca")
    assert result is None


def test_m05_update_existing_document():
    store = make_store()
    store.create_document("m05-test-003", make_reading(23.50))
    
    # Actualiza el registro con un nuevo valor válido
    nuevo_dato = make_reading(30.00)
    result = store.update_document("m05-test-003", nuevo_dato)
    assert result is True
    
    # Valida que los cambios se reflejen correctamente en la base de datos
    updated = store.get_document("m05-test-003")
    assert updated["value"] == 30.00


def test_m05_delete_document():
    store = make_store()
    store.create_document("m05-test-004", make_reading(20.00))
    
    # Ejecuta la eliminación del documento
    result = store.delete_document("m05-test-004")
    assert result is True
    
    # Confirma que el registro ya no se encuentre disponible
    assert store.get_document("m05-test-004") is None


def test_m05_duplicate_create_is_idempotent_upsert():
    store = make_store()
    first = make_reading(23.50)
    second = make_reading(25.00)

    # Crea dos registros consecutivos utilizando el mismo ID
    result1 = store.create_document("m05-duplicate-001", first)
    result2 = store.create_document("m05-duplicate-001", second)

    assert result1 == "m05-duplicate-001"
    assert result2 == "m05-duplicate-001"
    
    # Comprueba el comportamiento de sobrescritura (upsert) reteniendo el último valor
    saved = store.get_document("m05-duplicate-001")
    assert saved["value"] == 25.00


def test_m05_firestore_index_configuration():
    import json
    
    # Carga la configuración de índices requerida para el proyecto
    index_path = Path(__file__).resolve().parents[1] / "firestore.indexes.json"
    with open(index_path, encoding="utf-8") as file:
        config = json.load(file)

    indexes = config["indexes"]
    assert len(indexes) >= 1

    # Busca la configuración específica para la colección de telemetría
    telemetry_index = next(
        index for index in indexes
        if index["collectionGroup"] == "telemetry_events"
    )

    assert telemetry_index["queryScope"] == "COLLECTION"

    # Valida el ordenamiento correcto de los campos
    fields = telemetry_index["fields"]
    assert {"fieldPath": "device_id", "order": "ASCENDING"} in fields
    assert {"fieldPath": "timestamp", "order": "DESCENDING"} in fields