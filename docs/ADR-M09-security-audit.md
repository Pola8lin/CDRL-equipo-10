# ADR-M09 – Controles de acceso y auditoría

- **Estado:** Propuesto para revisión del equipo
- **Contexto:** M09 requiere controles por colección y operación, pruebas de abuso y auditoría sin secretos.
- **Decisión:** Aplicar permisos RBAC directamente en PostgreSQL mediante una migración incremental, sin modificar la migración histórica M03. Reader recibe SELECT; Writer recibe INSERT y uso de la secuencia; Operator recibe SELECT sobre la vista agregada; Migrator conserva administración. Se revoca CREATE del esquema public a PUBLIC.
- **Auditoría:** Emitir JSON con actor, acción, recurso y resultado (success, denied o error), más identificador y timestamp. No se incluyen consultas SQL, parámetros, payloads ni mensajes de excepción.
- **Remediación:** La política anterior concedía UPDATE a Writer. La migración M09 revoca los privilegios previos de los roles de aplicación y concede solo los mínimos necesarios. La prueba test_writer_cannot_update verifica el rechazo.
- **Consecuencias:** Las pruebas de permisos requieren PostgreSQL y usuarios sintéticos configurados localmente. La persistencia del logger depende de la configuración del despliegue; el código base emite al logger Python y no afirma que exista un almacén central de auditoría.
- **Verificación pendiente:** Ejecutar make setup, make verify y make run en el entorno Docker del equipo y adjuntar salidas reales antes de marcar la entrega como aprobada.
