import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class DocumentStore:
    def __init__(self):
        """Inicializa la conexión a Firestore de forma segura."""
        # Evita inicializar la app múltiples veces
        if not firebase_admin._apps:
            # Busca la ruta del archivo JSON de credenciales en el .env
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Si no hay ruta específica, usa las credenciales por defecto del entorno
                firebase_admin.initialize_app()
        
        # Conectar al cliente de Firestore y definir la colección principal
        self.db = firestore.client()
        self.collection_name = 'telemetry_events'

    def create_document(self, doc_id, data):
        """
        Crea un nuevo documento. 
        Si el doc_id ya existe, lo sobrescribe (comportamiento Upsert).
        """
        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        doc_ref.set(data)
        return doc_id

    def get_document(self, doc_id):
        """Consulta un documento por su ID."""
        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def update_document(self, doc_id, data):
        """Actualiza campos específicos de un documento que ya existe."""
        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        # update() falla si el documento no existe, lo cual es correcto para esta operación
        doc_ref.update(data)
        return True

    def delete_document(self, doc_id):
        """Elimina un documento de la colección."""
        doc_ref = self.db.collection(self.collection_name).document(doc_id)
        doc_ref.delete()
        return True