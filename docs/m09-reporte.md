# M09 – Controles de Acceso y Auditoría Útil

## 1. Objetivo
Diseñar controles por colección y operación, probar escenarios de abuso y demostrar una auditoría útil que no registre secretos ni datos sensibles.

## 2. Controles por Colección y Operación (RBAC)
Se implementó un modelo de control de acceso basado en roles directamente en el motor de base de datos (PostgreSQL), limitando las operaciones por tabla y tipo de acción:
- **Rol Writer:** Tiene permisos para ejecutar `INSERT` en la tabla de telemetría, pero no puede ejecutar `DELETE` ni `UPDATE`.
- **Rol Reader:** Tiene permisos exclusivos de lectura (`SELECT`), impidiendo cualquier mutación de datos.
- **Rol Operator:** Solo tiene acceso a la vista de resumen (`summary_view`), restringiendo por completo el acceso a la tabla principal de telemetría.

## 3. Auditoría sin Secretos
Se configuró un registro de auditoría estructurado que captura los eventos del sistema de forma segura. 
Cada registro de auditoría incluye:
- **Actor:** El rol o usuario que ejecuta la operación.
- **Acción:** El tipo de operación intentada.
- **Recurso:** La tabla o vista afectada.
- **Resultado:** Éxito o denegación de la transacción.

Para garantizar la seguridad, el sistema sanitiza automáticamente las cargas útiles antes de escribirlas en el log, omitiendo contraseñas, tokens o cadenas de conexión.

## 4. Pruebas y Remediación
La suite automatizada valida escenarios de abuso:
- **Caso normal:** El rol `writer` inserta telemetría correctamente.
- **Casos límite:** El `reader` consulta datos exitosamente; el `operator` accede al resumen sin ver la tabla base.
- **Fallo declarado y Remediación:** Cuando el rol `reader` intenta un `INSERT` (abuso de privilegios), la base de datos aborta la transacción mediante una política estricta y el sistema registra el rechazo en la auditoría. La remediación técnica consistió en revocar el esquema público por defecto y asignar permisos explícitos (Principio de Menor Privilegio).

## 5. Evidencia
Los resultados de estas reglas se demuestran en las pruebas `tests/test_permissions.py` y `tests/test_audit.py`. El reporte automatizado se guarda en `artifacts/pytest-results.xml`.