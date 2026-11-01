
from unittest.mock import MagicMock, patch

import pytest

from src.document_store import DocumentStore
from src.document_pagination import encode_cursor


class FakeDocument:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = True

    def to_dict(self):
        return self._data


def create_store():
    store = DocumentStore.__new__(DocumentStore)
    store.db = MagicMock()
    store.collection_name = "telemetry_events"
    return store


def test_first_page_returns_items_and_next_cursor():
    store = create_store()

    documents = [
        FakeDocument("doc-1", {"device_id": "sensor-01", "value": 10}),
        FakeDocument("doc-2", {"device_id": "sensor-01", "value": 20}),
        FakeDocument("doc-3", {"device_id": "sensor-01", "value": 30}),
    ]

    query = MagicMock()
    query.limit.return_value.stream.return_value = documents

    collection = store.db.collection.return_value
    collection.where.return_value.order_by.return_value.order_by.return_value = query

    with patch("src.document_store.FieldFilter"):
        result = store.get_documents_by_device_page(
            "sensor-01",
            page_size=2,
        )

    assert len(result["items"]) == 2
    assert result["has_more"] is True
    assert result["next_cursor"] == encode_cursor("sensor-01", "doc-2")


def test_last_page_has_no_next_cursor():
    store = create_store()

    documents = [
        FakeDocument("doc-1", {"device_id": "sensor-01", "value": 10}),
    ]

    query = MagicMock()
    query.limit.return_value.stream.return_value = documents

    collection = store.db.collection.return_value
    collection.where.return_value.order_by.return_value.order_by.return_value = query

    with patch("src.document_store.FieldFilter"):
        result = store.get_documents_by_device_page(
            "sensor-01",
            page_size=2,
        )

    assert len(result["items"]) == 1
    assert result["has_more"] is False
    assert result["next_cursor"] is None


def test_rejects_empty_device_id():
    store = create_store()

    with pytest.raises(ValueError, match="device_id"):
        store.get_documents_by_device_page("")


def test_rejects_missing_cursor_document():
    store = create_store()
    collection = store.db.collection.return_value

    missing_document = MagicMock()
    missing_document.exists = False
    collection.document.return_value.get.return_value = missing_document

    cursor = encode_cursor("sensor-01", "deleted-doc")

    with patch("src.document_store.FieldFilter"):
        with pytest.raises(ValueError, match="ya no existe"):
            store.get_documents_by_device_page(
                "sensor-01",
                page_size=2,
                cursor=cursor,
            )


def test_rejects_cursor_from_another_device():
    store = create_store()

    cursor = encode_cursor("sensor-02", "doc-1")

    with pytest.raises(ValueError, match="otro dispositivo"):
        store.get_documents_by_device_page(
            "sensor-01",
            page_size=2,
            cursor=cursor,
        )

def test_next_page_uses_previous_document_as_cursor():
    store = create_store()

    collection = store.db.collection.return_value

    last_document = FakeDocument(
        "doc-1",
        {"device_id": "sensor-01", "value": 10},
    )

    collection.document.return_value.get.return_value = last_document

    documents = [
        FakeDocument("doc-2", {"device_id": "sensor-01", "value": 20}),
        FakeDocument("doc-3", {"device_id": "sensor-01", "value": 30}),
    ]

    query = MagicMock()
    query.start_after.return_value = query
    query.limit.return_value.stream.return_value = documents

    collection.where.return_value.order_by.return_value.order_by.return_value = query

    cursor = encode_cursor("sensor-01", "doc-1")

    with patch("src.document_store.FieldFilter"):
        result = store.get_documents_by_device_page(
            "sensor-01",
            page_size=1,
            cursor=cursor,
        )

    query.start_after.assert_called_once_with(last_document)
    assert result["items"][0]["value"] == 20
    assert result["has_more"] is True
    assert result["next_cursor"] == encode_cursor("sensor-01", "doc-2")


def test_rejects_cursor_document_from_another_device():
    store = create_store()

    collection = store.db.collection.return_value

    wrong_document = FakeDocument(
        "doc-1",
        {"device_id": "sensor-02", "value": 10},
    )

    collection.document.return_value.get.return_value = wrong_document

    query = MagicMock()
    collection.where.return_value.order_by.return_value.order_by.return_value = query

    cursor = encode_cursor("sensor-01", "doc-1")

    with patch("src.document_store.FieldFilter"):
        with pytest.raises(ValueError, match="no corresponde"):
            store.get_documents_by_device_page(
                "sensor-01",
                page_size=2,
                cursor=cursor,
            )
