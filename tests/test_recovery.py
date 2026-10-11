import time
import pytest
from src.document_store import DocumentStore

def test_falla_controlada_y_recuperacion():
    print("\n--- INICIANDO SIMULACIÓN DE FALLA Y RECUPERACIÓN ---")
    store = DocumentStore()
    doc_id = "recovery-fixture-001"
    
    # Datos corregidos con la estructura obligatoria de telemetría
    fixture_data = {
        "device_id": "sensor-critico",
        "timestamp": "2026-10-11T12:00:00Z",
        "metric": "temperature",
        "value": 45.5,
        "unit": "°C"
    }
    
    # 1. Estado inicial estable
    store.create_document(doc_id, fixture_data)
    
    # 2. Diseñar falla controlada
    store.delete_document(doc_id)
    assert store.get_document(doc_id) is None, "Falla inducida: Datos eliminados."
    
    # 3. Medir tiempo de recuperación
    start_time = time.time()
    store.create_document(doc_id, fixture_data)
    end_time = time.time()
    
    recovery_time = end_time - start_time
    
    # 4. Verificar los registros recuperados
    recovered_data = store.get_document(doc_id)
    assert recovered_data is not None, "El documento no se recuperó."
    assert recovered_data["device_id"] == "sensor-critico", "Datos corruptos tras recuperación."
    
    print(f"Recuperación exitosa. Tiempo medido: {recovery_time:.4f} segundos.")
    
    # Limpieza final
    store.delete_document(doc_id)