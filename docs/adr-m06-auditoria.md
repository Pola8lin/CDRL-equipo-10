# ADR M06: Registro de Auditoría y Protección de Secretos

## Contexto
El sistema requiere trazabilidad de las operaciones (CREATE, UPDATE, DELETE) en la base de datos, permitiendo saber quién hizo qué y cuándo. Sin embargo, se debe garantizar que ninguna credencial, token o cadena de conexión se filtre accidentalmente en los registros.

## Decisión
Se implementará la clase `AuditLogger` en `src/audit.py`. Esta clase tendrá la responsabilidad dual de:
1. Generar un esquema de auditoría estándar (`auditId`, `timestamp`, `actorId`, `action`, etc.).
2. Ejecutar una función de sanitización (enmascaramiento) sobre los datos antes de registrarlos, interceptando claves como `password`, `token` o `api_key` y reemplazándolas por `*****`.

## Consecuencias
* Garantizamos la auditoría del sistema para análisis post-mortem.
* Cumplimos con los requisitos de seguridad al evitar la persistencia de texto plano en los logs.