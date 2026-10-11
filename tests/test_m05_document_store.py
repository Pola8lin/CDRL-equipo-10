import sys
from unittest.mock import MagicMock
from pathlib import Path

import pytest
from firebase_admin import firestore


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
    """Crea un almacén en memoria para las pruebas unitarias CRUD."""
    documents = {}

    class FakeSnapshot:
        def __init__(self, data):
            self.exists = data is not None
            self._data = data

        def to_dict(self):
            return dict(self._data) if self._data is not None else None

    class FakeDocumentRef:
        def __init__(self, doc_id):
            self.doc_id = doc_id

        def get(self):
            return FakeSnapshot(documents.get(self.doc_id))

        def set(self, data):
            documents[self.doc_id] = dict(data)

        def update(self, data):
            if self.doc_id not in documents:
                raise ValueError("El documento no existe.")
            documents[self.doc_id].update(data)

        def delete(self):
            documents.pop(self.doc_id, None)

    class FakeCollection:
        def document(self, doc_id):
            return FakeDocumentRef(doc_id)

    class FakeDB:
        def collection(self, name):
            assert name == "telemetry_events"
            return FakeCollection()

    store = DocumentStore.__new__(DocumentStore)
    store.db = FakeDB()
    store.collection_name = "telemetry_events"
    return store


def make_mock_store():
    """Crea un almacén con mocks para comprobar llamadas específicas."""
    store = DocumentStore.__new__(DocumentStore)
    store.db = MagicMock()
    store.collection_name = "telemetry_events"
    return store




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


def test_m05_update_validates_merged_document():
    store = make_mock_store()
    doc_ref = store.db.collection.return_value.document.return_value

    existing_document = MagicMock()
    existing_document.exists = True
    existing_document.to_dict.return_value = make_reading(23.50)
    doc_ref.get.return_value = existing_document

    result = store.update_document(
        "m05-test-001",
        {"value": 30.00},
    )

    assert result is True
    doc_ref.get.assert_called_once()
    doc_ref.update.assert_called_once_with({"value": 30.00})


def test_get_documents_by_device_filters_and_orders_by_timestamp():
    store = make_mock_store()
    collection = store.db.collection.return_value
    filtered_query = collection.where.return_value
    ordered_query = filtered_query.order_by.return_value

    older = {
        "device_id": "sensor-m05-test",
        "timestamp": "2026-10-01T09:30:00Z",
        "metric": "temperature",
        "value": 22.0,
        "unit": "?C",
    }
    newer = {
        "device_id": "sensor-m05-test",
        "timestamp": "2026-10-01T10:30:00Z",
        "metric": "temperature",
        "value": 23.5,
        "unit": "?C",
    }

    older_doc = MagicMock()
    older_doc.to_dict.return_value = older
    newer_doc = MagicMock()
    newer_doc.to_dict.return_value = newer
    ordered_query.stream.return_value = [newer_doc, older_doc]

    result = store.get_documents_by_device("sensor-m05-test")

    collection.where.assert_called_once()
    filtered_query.order_by.assert_called_once_with(
        "timestamp",
        direction=firestore.Query.DESCENDING,
    )
    assert result == [newer, older]


def test_get_documents_by_device_rejects_empty_device_id():
    store = make_mock_store()

    with pytest.raises(ValueError, match="device_id"):
        store.get_documents_by_device("")

    store.db.collection.assert_not_called()
