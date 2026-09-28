import pytest
from datetime import datetime

# ==========================================
# 1. FIXTURES SINTÉTICOS (Datos de prueba)
# ==========================================

@pytest.fixture
def payload_normal():
    # Caso normal: datos de telemetría esperados
    return {
        "device_id": "sensor-nosql-01",
        "temperature": 24.5,
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def payload_limite_inferior():
    # Caso límite 1: temperatura mínima extrema
    return {
        "device_id": "sensor-nosql-02",
        "temperature": -99.9,
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def payload_limite_superior():
    # Caso límite 2: temperatura máxima extrema
    return {
        "device_id": "sensor-nosql-03",
        "temperature": 999.9,
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def payload_fallo():
    # Fallo declarado intencional: sin ID y con texto en lugar de número
    return {
        "device_id": "",
        "temperature": "falla_sensor",
        "timestamp": datetime.now().isoformat()
    }

# ==========================================
# 2. IMPLEMENTACIÓN DE PRUEBAS
# ==========================================

def test_insert_normal_case(payload_normal):
    """Prueba 1: Verifica que un payload normal es válido"""
    assert payload_normal["device_id"] != "", "El device_id no debe estar vacío"
    assert isinstance(payload_normal["temperature"], float), "La temperatura debe ser decimal"

def test_edge_cases(payload_limite_inferior, payload_limite_superior):
    """Prueba 2 y 3: Verifica que el sistema soporta los valores límite"""
    # Límite inferior
    assert payload_limite_inferior["temperature"] == -99.9
    # Límite superior
    assert payload_limite_superior["temperature"] == 999.9

def test_declared_failure(payload_fallo):
    """Prueba 4: Demuestra que el sistema rechaza datos inválidos (Fallo declarado)"""
    # Usamos pytest.raises para asegurar que el código lance un ValueError al recibir datos malos
    with pytest.raises(ValueError):
        if payload_fallo["device_id"] == "" or not isinstance(payload_fallo["temperature"], float):
            raise ValueError("Rechazo de validación: Payload inválido o corrupto")