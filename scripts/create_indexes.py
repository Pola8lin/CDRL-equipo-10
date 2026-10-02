import os
import pymongo
from pymongo import IndexModel, ASCENDING, DESCENDING
from dotenv import load_dotenv

# Cargar variables de entorno (no hardcodear secretos)
load_dotenv()

def get_database():
    """Establece la conexión usando variables de entorno."""
    client = pymongo.MongoClient(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 27017)),
        username=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "password")
    )
    return client[os.getenv("DB_NAME", "cdrl_document_store")]

def create_indexes(db):
    """
    Crea los índices necesarios de forma idempotente.
    En MongoDB, create_indexes es idempotente por defecto: si el índice ya existe, no hace nada.
    """
    coleccion = db["telemetry"]

    # 1. Índice para búsquedas exactas por dispositivo
    # Justificación: Acelera las consultas donde filtramos lecturas de un sensor específico.
    index_device = IndexModel([("device_id", ASCENDING)], name="idx_device_id")

    # 2. Índice compuesto para búsquedas por dispositivo ordenadas por tiempo
    # Justificación: Optimiza las consultas de series temporales (ej. "últimas 10 lecturas del sensor X").
    index_device_time = IndexModel(
        [("device_id", ASCENDING), ("timestamp", DESCENDING)], 
        name="idx_device_timestamp"
    )

    print("Creando índices en la colección 'telemetry'...")
    # Ejecuta la creación (Idempotente)
    coleccion.create_indexes([index_device, index_device_time])
    print("Índices creados/verificados exitosamente.")

if __name__ == "__main__":
    db = get_database()
    create_indexes(db)