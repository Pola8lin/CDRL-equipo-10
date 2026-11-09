"""Auditoría estructurada: registra metadatos, nunca cargas útiles."""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Callable, TypeVar

T = TypeVar("T")
_AUDIT_LOGGER = logging.getLogger("cdrl.audit")


class AuditLogger:
    """Emite eventos sin incluir parámetros SQL ni datos de documentos."""

    VALID_RESULTS = {"success", "denied", "error"}

    def create_audit_record(
        self,
        actor: str,
        action: str,
        resource: str,
        result: str,
    ) -> dict:
        fields = {
            "actor": actor,
            "action": action,
            "resource": resource,
            "result": result,
        }
        if any(not isinstance(value, str) or not value.strip()
               for value in fields.values()):
            raise ValueError("actor, action, resource y result son obligatorios")
        if result not in self.VALID_RESULTS:
            raise ValueError("result debe ser success, denied o error")

        return {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action.upper(),
            "resource": resource,
            "result": result,
        }

    def log_event(
        self,
        actor: str,
        action: str,
        resource: str,
        result: str,
    ) -> dict:
        """Escribe únicamente los cuatro metadatos requeridos y el timestamp."""
        record = self.create_audit_record(actor, action, resource, result)
        _AUDIT_LOGGER.info(
            json.dumps(record, ensure_ascii=False, sort_keys=True)
        )
        return record

    def run_audited(
        self,
        actor: str,
        action: str,
        resource: str,
        operation: Callable[[], T],
    ) -> T:
        """Ejecuta una operación y audita éxito, denegación SQL o error.

        No registra el mensaje de excepción ni los parámetros de la operación,
        porque podrían contener datos sensibles.
        """
        try:
            result = operation()
        except Exception as exc:
            sqlstate = getattr(exc, "sqlstate", None)
            outcome = "denied" if sqlstate == "42501" else "error"
            self.log_event(actor, action, resource, outcome)
            raise
        else:
            self.log_event(actor, action, resource, "success")
            return result
