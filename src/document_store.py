import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

from src.validator import validate_telemetry

# Cargar las variables de entorno para no dejar rutas fijas en el código
load_dotenv()

class DocumentStore:
    def __init__(self):
        """Inicializa la conexión a Firestore."""
        # Validar que la app no esté ya iniciada para evitar errores de Firebase
        if not firebase_admin._apps:
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            
            # Si hay una ruta configurada en el .env, usa ese archivo JSON
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # En la nube usa las credenciales automáticas del servidor
                firebase_admin.initialize_app()
        
        # Conexión principal a la base de datos y la colección
        self.db = firestore.client()
        self.collection_name = 'telemetry_events'

    def create_document(self, doc_id, data):
        """Crea un documento o lo sobreescribe si ya existe."""
        # Asegurar que la información cumpla con las reglas antes de escribir
        es_valido, errores = validate_telemetry(data)
        if not es_valido:
            raise ValueError(f"No se puede guardar. Datos inválidos: {', '.join(errores)}")

        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        doc_ref.set(data)
        return doc_id

    def get_document(self, doc_id):
        """Obtiene un documento usando su ID."""
        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        doc = doc_ref.get()
        
        # Si el documento existe, lo regresamos como diccionario
        if doc.exists:
            return doc.to_dict()
        return None

    def update_document(self, doc_id, data):
        """Actualiza campos específicos de un registro."""
        # También pasamos los datos por el validador en las actualizaciones
        es_valido, errores = validate_telemetry(data)
        if not es_valido:
            raise ValueError(f"No se puede actualizar. Datos inválidos: {', '.join(errores)}")

        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        doc_ref.update(data)
        return True

    def delete_document(self, doc_id):
        """Elimina el registro de Firestore."""
        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        doc_ref.delete()
        return True