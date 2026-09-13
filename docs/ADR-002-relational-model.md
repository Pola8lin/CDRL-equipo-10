# ADR-002 — Diseño de Restricciones y Pruebas del Modelo Relacional

## Estado

Aceptado

## Contexto

Para el hito M02 del proyecto CDRL, es imperativo garantizar la integridad de los datos de telemetría directamente en la capa de persistencia (PostgreSQL). Independientemente de la validación a nivel de aplicación (Python), la base de datos debe asegurar el cumplimiento de las invariantes del modelo relacional para evitar la inserción de registros anómalos o corruptos.

## Decisión

El equipo ha decidido implementar restricciones estructurales (DDL) estrictas en la tabla `telemetry_reading`:

* **Idempotencia:** Se implementa la cláusula `CREATE TABLE IF NOT EXISTS` en las migraciones para garantizar que los scripts de despliegue puedan ejecutarse múltiples veces sin generar conflictos en los entornos de desarrollo (Docker Compose) y producción.
* **Integridad de Dominio:** 
  * Se restringe la columna `value` mediante `CHECK (value >= -50.00 AND value <= 100.00)` para rechazar lecturas fuera de los umbrales operativos.
  * Se limitan estrictamente los campos `metric` a `'temperature'` y `unit` a `'°C'` mediante restricciones `CHECK`.
* **Validación de Identidad:** Se aplica la restricción `CHECK (TRIM(device_id) <> '')` combinada con `NOT NULL` para impedir el registro de identificadores vacíos o compuestos únicamente por espacios en blanco.

## Pruebas y Validación

El diseño del modelo relacional fue sometido a pruebas directas en el motor de base de datos para comprobar los siguientes casos:
* **Caso normal y límites:** Valores válidos (ej. 23.50) y valores en los límites exactos (-50.00 y 100.00) son aceptados exitosamente.
* **Fallos declarados:** 
  * **Fuera de rango:** El valor 100.01 es rechazado de forma determinista por la restricción `telemetry_reading_value_check`.
  * **Caso vacío:** Una cadena vacía o de espacios en el `device_id` es rechazada por `telemetry_reading_device_id_check`.

## Consecuencias

### Positivas
* Integridad de datos absoluta garantizada a nivel del motor de base de datos.
* Prevención de fallos silenciosos ante hardware defectuoso que envíe métricas irreales.
* Cumplimiento estricto del contrato de datos establecido en M01.

### Negativas
* **Alta rigidez del esquema:** La integración futura de nuevas métricas (por ejemplo, humedad) o unidades de medida requerirá forzosamente la creación de nuevas migraciones DDL para modificar las restricciones `CHECK` existentes.