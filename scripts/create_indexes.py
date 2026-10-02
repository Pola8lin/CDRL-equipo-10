import json
import os

def generate_firestore_indexes():
    """
    En Firebase/Firestore, los índices de un solo campo son automáticos.
    Este script genera el archivo de configuración para los índices compuestos
    necesarios para las consultas ordenadas por tiempo.
    """
    indexes = {
        "indexes": [
            {
                "collectionGroup": "telemetry_events",
                "queryScope": "COLLECTION",
                "fields": [
                    {"fieldPath": "device_id", "order": "ASCENDING"},
                    {"fieldPath": "timestamp", "order": "DESCENDING"}
                ]
            }
        ],
        "fieldOverrides": []
    }
    
    # Generar el archivo en la raíz del proyecto
    with open("firestore.indexes.json", "w") as f:
        json.dump(indexes, f, indent=2)
    
    print("Éxito: Archivo firestore.indexes.json generado.")
    print("Justificación: Se requiere un índice compuesto para buscar por 'device_id' y ordenar por 'timestamp'.")
    print("Para desplegar este índice en la nube ejecuta: firebase deploy --only firestore:indexes")

if __name__ == "__main__":
    generate_firestore_indexes()