import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa Firebase (asume que la variable GOOGLE_APPLICATION_CREDENTIALS está configurada)
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

db = firestore.client()
coleccion = db.collection("telemetry_events")

def run_tests():
    print("--- PREPARACIÓN ---")
    doc_ref_1 = coleccion.document("test_doc_1")
    doc_ref_2 = coleccion.document("test_doc_2")
    # Limpiamos antes de la prueba
    doc_ref_1.delete()
    doc_ref_2.delete()

    print("--- 1. CONSULTA NORMAL ---")
    doc_ref_1.set({"device_id": "sensor-alpha", "temp": 25.0, "timestamp": "2026-10-02T10:00:00Z"})
    resultados = list(coleccion.where("device_id", "==", "sensor-alpha").stream())
    print(f"Éxito. Documentos encontrados: {len(resultados)}")

    print("\n--- 2. AUSENCIA DE DOCUMENTO ---")
    resultados_vacios = list(coleccion.where("device_id", "==", "sensor-fantasma").stream())
    assert len(resultados_vacios) == 0
    print("Éxito. La consulta para un sensor inexistente retorna una lista vacía.")

    print("\n--- 3. DUPLICADOS E IDEMPOTENCIA ---")
    # En Firestore, .set() sobrescribe si el ID ya existe, haciéndolo idempotente por naturaleza.
    payload = {"device_id": "sensor-beta", "temp": 30.0, "timestamp": "2026-10-02T10:05:00Z"}
    
    # Ejecutamos la inserción dos veces
    doc_ref_2.set(payload)
    doc_ref_2.set(payload)
    
    # Verificamos que no se crearon documentos duplicados (debe haber solo 1)
    res_idempotencia = list(coleccion.where("device_id", "==", "sensor-beta").stream())
    assert len(res_idempotencia) == 1
    print(f"Éxito. Operación idempotente confirmada. Registros totales creados: {len(res_idempotencia)}")

if __name__ == "__main__":
    run_tests()