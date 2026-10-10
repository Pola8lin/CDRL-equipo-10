from src.audit import AuditLogger

def test_estructura_registro_auditoria():
    """Verifica que el registro se cree con los datos básicos correctos."""
    logger = AuditLogger()
    record = logger.create_audit_record(
        actor_id="dev-ismael", 
        action="DELETE", 
        target_collection="telemetry_data", 
        document_id="SENSOR-001"
    )
    
    # Comprobamos que sí se generen el ID y la fecha
    assert "auditId" in record
    assert "timestamp" in record
    
    # Comprobamos que guarde bien al usuario y la acción
    assert record["actorId"] == "dev-ismael"
    assert record["action"] == "DELETE"

def test_sanitizacion_de_secretos():
    """Comprueba que el sistema esconda las contraseñas y no las deje pasar."""
    logger = AuditLogger()
    
    # Simulamos datos que alguien intenta guardar, mezclando cosas normales y secretas
    datos_peligrosos = {
        "temperature": 28.5,
        "password": "MiContraseñaSecreta123",
        "api_key": "AIzaSyB-12345",
        "sessionToken": "abc123xyz"
    }
    
    record = logger.create_audit_record(
        actor_id="dev-ismael", 
        action="UPDATE", 
        target_collection="users", 
        document_id="USER-88", 
        payload=datos_peligrosos
    )
    
    # Un dato normal como la temperatura sí debe pasar tal cual
    assert record["payload"]["temperature"] == 28.5
    
    # Los datos secretos deben aparecer censurados con asteriscos
    assert record["payload"]["password"] == "*****"
    assert record["payload"]["api_key"] == "*****"
    assert record["payload"]["sessionToken"] == "*****"
    
    # Verificamos que la contraseña original de verdad no se haya colado en ningún lado
    assert "MiContraseñaSecreta123" not in str(record)