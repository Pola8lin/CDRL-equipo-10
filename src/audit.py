import uuid
from datetime import datetime, timezone

class AuditLogger:
    def __init__(self):
        # Palabras prohibidas que nunca deben quedar guardadas en la base de datos
        self.secret_keys = ['password', 'token', 'api_key', 'secret', 'credentials', 'connection_string']

    def sanitize_payload(self, payload: dict) -> dict:
        """Revisa los datos y oculta contraseñas o tokens antes de guardarlos."""
        sanitized = {}
        for key, value in payload.items():
            # Si la llave es algo secreto (como 'password'), la cambiamos por asteriscos
            if any(secret in key.lower() for secret in self.secret_keys):
                sanitized[key] = "*****"
            else:
                sanitized[key] = value
        return sanitized

    def create_audit_record(self, actor_id: str, action: str, target_collection: str, document_id: str, payload: dict = None) -> dict:
        """Crea el registro de qué pasó, quién lo hizo y cuándo."""
        record = {
            "auditId": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actorId": actor_id,
            "action": action.upper(),
            "targetCollection": target_collection,
            "documentId": document_id,
        }
        
        # Si la operación trae información adicional (por ejemplo, datos nuevos en un UPDATE), 
        # pasamos esos datos por el filtro de seguridad antes de agregarlos al registro.
        if payload:
            record["payload"] = self.sanitize_payload(payload)
            
        return record