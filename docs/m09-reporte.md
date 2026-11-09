# M09 – Controles de acceso y auditoría útil

## Objetivo
Aplicar permisos por colección y operación, probar intentos de abuso y emitir eventos de auditoría útiles sin guardar secretos.

## Modelo de permisos
La migración histórica `03_security_roles.sql` conserva el contexto M03. La corrección específica M09 se aplica mediante `05_m09_security_hardening.sql`, sin reescribir la migración histórica.

| Rol | Recurso | Permisos |
|---|---|---|
| `cdrl_reader` | `public.telemetry_reading` | SELECT |
| `cdrl_writer` | `public.telemetry_reading` | INSERT y uso de secuencia |
| `cdrl_operator` | `public.telemetry_summary` | SELECT |
| `cdrl_migrator` | tabla y secuencia | administración |

Los permisos se aplican en PostgreSQL. Writer no debe poder leer, actualizar ni borrar la tabla. Operator no debe poder consultar la tabla base.

## Auditoría
`src/audit.py` emite JSON estructurado con `actor`, `action`, `resource`, `result`, identificador y timestamp. Los resultados válidos son `success`, `denied` y `error`.

El envoltorio `run_audited` registra éxito o excepción. Solo clasifica como `denied` una excepción PostgreSQL con SQLSTATE `42501`; otras excepciones se clasifican como `error`. La excepción original se vuelve a lanzar.

Por diseño, el evento no incluye SQL, parámetros, payload, mensajes de excepción ni credenciales. Así se evita depender de una lista parcial de nombres de campos secretos.

## Casos de prueba
- Normal: Writer inserta una lectura sintética; Reader consulta; Operator consulta la vista.
- Límites: Writer no puede leer ni actualizar; Reader no puede borrar; Operator no puede leer la tabla base.
- Abuso/fallo declarado: Reader intenta INSERT y PostgreSQL debe devolver privilegio insuficiente (SQLSTATE 42501); el envoltorio emite resultado `denied`.

Las pruebas de permisos requieren PostgreSQL local y las contraseñas sintéticas configuradas en `.env` a partir de `.env.example`.

## Remediación
La condición vulnerable era que la política anterior otorgaba a Writer `SELECT, INSERT, UPDATE`, además de repetir el GRANT. La migración M09 revoca los privilegios de los roles de aplicación y concede únicamente los permisos definidos en la matriz anterior. Es idempotente y se ejecuta desde `scripts/db_setup.py`.

La prueba `test_writer_cannot_update` verifica la denegación posterior a la remediación. También se prueban los límites de lectura y borrado.

## Ejecución y evidencia
Ejecutar en el entorno del equipo:

```bash
make setup
make verify
make run
```

El resultado verificable debe guardarse en `artifacts/m09-security-results.json` y la salida JUnit en `artifacts/pytest-results.xml`. No declarar aprobado hasta ejecutar estos comandos y conservar los resultados reales.

## Limitaciones
La auditoría implementada emite eventos al logger Python; su persistencia y envío a un colector central dependen de la configuración de logging del despliegue. Las pruebas unitarias validan el formato y la ausencia de cargas útiles; las pruebas PostgreSQL validan permisos y el registro del resultado en el logger durante la ejecución de la operación.
