import os

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from src.validator import validate_telemetry

# Carga las variables de entorno del proyecto.
load_dotenv()


class DocumentStore:
    def __init__(self):
        """Inicializa la conexi?n a Firestore."""
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

            if cred_path and os.path.isfile(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Usa las credenciales predeterminadas del entorno.
                firebase_admin.initialize_app()

        self.db = firestore.client()
        self.collection_name = "telemetry_events"

    def create_document(self, doc_id, data):
        """Valida y guarda un documento de telemetr?a."""
        valid, errors = validate_telemetry(data)
        if not valid:
            raise ValueError(
                "No se puede guardar la lectura: " + "; ".join(errors)
            )

        doc_ref = (
            self.db.collection(self.collection_name)
            .document(doc_id)
        )
        doc_ref.set(data)
        return doc_id

    def get_document(self, doc_id):
        """Obtiene un documento por su ID."""
        doc_ref = (
            self.db.collection(self.collection_name)
            .document(doc_id)
        )
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()

        return None

    def get_documents_by_device(self, device_id):
        """Obtiene las lecturas de un dispositivo, de m?s reciente a m?s antigua."""
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError("device_id debe ser una cadena no vac?a.")

        query = (
            self.db.collection(self.collection_name)
            .where(filter=FieldFilter("device_id", "==", device_id))
            .order_by(
                "timestamp",
                direction=firestore.Query.DESCENDING,
            )
        )

        return [document.to_dict() for document in query.stream()]

    def update_document(self, doc_id, data):
        """Valida el documento completo antes de actualizarlo."""
        doc_ref = (
            self.db.collection(self.collection_name)
            .document(doc_id)
        )

        current_doc = doc_ref.get()
        if not current_doc.exists:
            raise ValueError(f"El documento '{doc_id}' no existe.")

        current_data = current_doc.to_dict() or {}
        updated_data = {**current_data, **data}

        valid, errors = validate_telemetry(updated_data)
        if not valid:
            raise ValueError(
                "No se puede actualizar la lectura: " + "; ".join(errors)
            )

        doc_ref.update(data)
        return True

    def delete_document(self, doc_id):
        """Elimina un documento de la colecci?n."""
        doc_ref = (
            self.db.collection(self.collection_name)
            .document(doc_id)
        )
        doc_ref.delete()
        return True
