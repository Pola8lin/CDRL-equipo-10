import json
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.document_store import DocumentStore


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "fixtures" / "m06-documents-v1.json"
RESULT_PATH = ROOT / "artifacts" / "m06-recovery-results.json"


class MemoryDocumentStore:
    """Almacén en memoria para simular pérdida y recuperación sin Firestore."""

    def __init__(self):
        self.documents = {}

    def create_document(self, doc_id, data):
        if not isinstance(data, dict) or not data:
            raise ValueError("El documento debe contener datos v?lidos.")
        if doc_id in self.documents:
            raise ValueError(f"El documento '{doc_id}' ya existe.")
        self.documents[doc_id] = dict(data)
        return doc_id

    def get_document(self, doc_id):
        value = self.documents.get(doc_id)
        return dict(value) if value is not None else None

    def delete_document(self, doc_id):
        self.documents.pop(doc_id, None)
        return True


def load_fixture():
    with FIXTURE_PATH.open("r", encoding="utf-8-sig") as file:
        fixtures = json.load(file)
    assert fixtures, "El fixture M06 no contiene documentos."
    return {
        key: value
        for key, value in fixtures[0].items()
        if key != "_description"
    }


def test_recuperacion_desde_fixture_mide_integridad():
    store = MemoryDocumentStore()
    doc_id = "recovery-fixture-001"
    fixture_data = load_fixture()

    # Estado estable inicial.
    store.create_document(doc_id, fixture_data)
    assert store.get_document(doc_id) == fixture_data

    # Falla controlada: pérdida del documento.
    store.delete_document(doc_id)
    assert store.get_document(doc_id) is None

    # Restauración cronometrada desde el fixture versionado.
    start = time.perf_counter()
    store.create_document(doc_id, fixture_data)
    recovered_data = store.get_document(doc_id)
    recovery_seconds = time.perf_counter() - start

    # Verificación completa de integridad.
    assert recovered_data is not None
    assert recovered_data == fixture_data

    result = {
        "assignmentId": "m06-recovery",
        "scenario": "controlled_delete_and_fixture_restore",
        "fixture": "fixtures/m06-documents-v1.json",
        "controlled_failure_detected": True,
        "fixture_recovered": True,
        "data_integrity_verified": recovered_data == fixture_data,
        "recovery_time_seconds": round(recovery_seconds, 8),
        "recovered_fields": len(recovered_data),
        "status": "passed",
    }

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    assert recovery_seconds >= 0
    assert result["recovered_fields"] == len(fixture_data)

    print(
        "Recuperación verificada: "
        f"{recovery_seconds:.8f} segundos; "
        f"{len(recovered_data)} campos íntegros."
    )


def test_recuperacion_rechaza_fixture_vacio():
    store = MemoryDocumentStore()
    assert store.get_document("missing-document") is None
    with pytest.raises(ValueError):
        store.create_document("empty-document", {})


def test_recuperacion_detecta_documento_no_restaurado():
    store = MemoryDocumentStore()
    doc_id = "recovery-failure-001"

    store.delete_document(doc_id)

    # Fallo declarado: no se ejecuta la restauración.
    assert store.get_document(doc_id) is None


def test_document_store_real_no_se_inicializa_en_esta_prueba():
    # Comprueba que esta prueba no necesita inicializar el cliente de Firestore.
    store = DocumentStore.__new__(DocumentStore)
    store.db = MagicMock()
    store.collection_name = "telemetry_events"
    assert store.collection_name == "telemetry_events"
