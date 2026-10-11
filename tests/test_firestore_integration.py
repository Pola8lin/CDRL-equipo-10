import os
import uuid
from pathlib import Path

import pytest

from src.document_store import DocumentStore


def has_firebase_credentials():
    """Check for configured credentials without exposing secrets."""
    path = (
        os.getenv("FIREBASE_CREDENTIALS_PATH")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    return bool(path and Path(path).is_file())


def test_firestore_real_crud_and_indexed_query():
    if not has_firebase_credentials():
        if os.getenv("CI", "").lower() == "true":
            pytest.fail(
                "CI requires accessible credentials for real Firestore integration."
            )
        pytest.skip("No local Firestore credentials are available")

    store = DocumentStore()
    suffix = uuid.uuid4().hex
    device_id = f"test-integration-{suffix}"
    doc_old = f"test-old-{suffix}"
    doc_new = f"test-new-{suffix}"

    older = {
        "device_id": device_id,
        "timestamp": "2026-10-01T09:30:00Z",
        "metric": "temperature",
        "value": 22.0,
        "unit": "\u00b0C",
    }
    newer = {
        "device_id": device_id,
        "timestamp": "2026-10-01T10:30:00Z",
        "metric": "temperature",
        "value": 23.5,
        "unit": "\u00b0C",
    }

    try:
        store.create_document(doc_old, older)
        store.create_document(doc_new, newer)

        assert store.get_document(doc_old) == older

        store.update_document(doc_old, {"value": 24.0})
        updated = store.get_document(doc_old)
        assert updated["value"] == 24.0

        results = store.get_documents_by_device(device_id)

        assert len(results) == 2
        assert results[0]["timestamp"] > results[1]["timestamp"]
        assert all(item["device_id"] == device_id for item in results)
    finally:
        store.delete_document(doc_old)
        store.delete_document(doc_new)
