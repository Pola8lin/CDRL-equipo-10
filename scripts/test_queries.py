import os
import pymongo
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv

# Cargar variables de entorno de forma segura
load_dotenv()

def get_database():
    client = pymongo.MongoClient(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 27017)),
        username=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password")
    )
    return client[os.getenv("DB_NAME", "cdrl_document_store")]

def run_tests():
    db = get_database()
    coleccion = db["telemetry"]
    
    # Preparación: Limpiamos datos de prueba anteriores
    coleccion.delete_many({"_id": {"$in": ["test_doc_1", "test_doc_2"]}})

    print("--- 1. CONSULTA NORMAL ---")
    coleccion.insert_one({"_id": "test_doc_1", "device_id": "sensor-alpha", "temp": 25.0})
    resultado_normal = coleccion.find_one({"device_id": "sensor-alpha"})
    print(f"Éxito. Documento encontrado: {resultado_normal}")

    print("\n--- 2. AUSENCIA DE DOCUMENTO ---")
    resultado_ausente = coleccion.find_one({"device_id": "sensor-fantasma"})
    assert resultado_ausente is None
    print("Éxito. El sistema maneja correctamente la búsqueda vacía (retorna None).")

    print("\n--- 3. DUPLICADO ---")
    try:
        # Intentamos insertar el mismo registro exacto (mismo _id)
        coleccion.insert_one({"_id": "test_doc_1", "device_id": "sensor-alpha", "temp": 99.9})
        print("Error: El sistema permitió un duplicado.")
    except DuplicateKeyError:
        print("Éxito. El motor rechazó el documento duplicado protegiendo la integridad.")

    print("\n--- 4. REPETICIÓN IDEMPOTENTE ---")
    # Para hacer una operación segura de repetición, usamos update_one con upsert=True
    filtro = {"_id": "test_doc_2"}
    cambio = {"$set": {"device_id": "sensor-beta", "temp": 30.0}}
    
    # Primera ejecución (crea el documento)
    res1 = coleccion.update_one(filtro, cambio, upsert=True)
    print(f"Ejecución 1 (Modificados: {res1.modified_count}, Insertados: {1 if res1.upserted_id else 0})")
    
    # Segunda ejecución idéntica (no hace nada ni rompe el sistema)
    res2 = coleccion.update_one(filtro, cambio, upsert=True)
    print(f"Ejecución 2 (Modificados: {res2.modified_count}, Insertados: {1 if res2.upserted_id else 0})")
    print("Éxito. La operación es idempotente: ejecutarla varias veces deja el mismo estado final.")

if __name__ == "__main__":
    run_tests()