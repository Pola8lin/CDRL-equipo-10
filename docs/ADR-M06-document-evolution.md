# ADR-M06: Evolución de documentos de telemetría

**Estado:** Propuesta implementada y probada
**Semana:** M06 — Consulta, evolución, auditoría y recuperación
**Decisión:** Utilizar versiones explícitas de esquema para evolucionar documentos.

## 1. Contexto

En M05 se implementó un almacén de documentos para lecturas de telemetría en Firestore. Cada lectura contiene los campos `device_id`, `timestamp`, `metric`, `value` y `unit`.

Cuando una aplicación evoluciona, la estructura de sus documentos puede cambiar. Es necesario definir una estrategia que permita reconocer los documentos antiguos, convertirlos a la nueva estructura y evitar que datos inválidos se acepten durante el proceso.

## 2. Decisión

Se implementó un módulo independiente llamado `src/document_evolution.py` para convertir documentos de la versión 1 a la versión 2.

La versión 1 contiene directamente los campos de la lectura. La versión 2 incorpora el campo `schema_version` y agrupa los datos dentro de `reading`.

La función de migración reutiliza `validate_telemetry()` para conservar las reglas de validación existentes. También verifica la versión de origen y devuelve un error cuando los datos son inválidos o la versión no es compatible.

## 3. Ejemplo de evolución

**Versión 1:**

```json
{
  "device_id": "sensor-m06-001",
  "timestamp": "2026-10-01T10:30:00Z",
  "metric": "temperature",
  "value": 23.5,
  "unit": "°C"
}
```

**Versión 2:**

```json
{
  "schema_version": 2,
  "reading": {
    "device_id": "sensor-m06-001",
    "timestamp": "2026-10-01T10:30:00Z",
    "metric": "temperature",
    "value": 23.5,
    "unit": "°C"
  }
}
```

## 4. Alternativas consideradas

* **Mantener únicamente la estructura antigua:** es sencillo, pero no identifica explícitamente la versión del esquema.
* **Reemplazar los documentos antiguos directamente:** podría dificultar la compatibilidad con consumidores que todavía esperan la estructura anterior.
* **Agregar una versión explícita y una función de migración:** permite identificar el esquema, validar los datos y probar la conversión sin modificar los documentos originales.

Se eligió la tercera alternativa.

## 5. Pruebas realizadas

Se creó `tests/test_document_evolution.py` con cuatro pruebas automatizadas:

1. Migración correcta de un documento válido.
2. Rechazo de una temperatura fuera del rango permitido.
3. Rechazo de una versión de origen no compatible.
4. Rechazo de un documento al que le falta un campo obligatorio.

**Resultado obtenido:** 4 pruebas aprobadas en `0.07 segundos`, mediante `python -m pytest tests/test_document_evolution.py -v`.

## 6. Alcance y limitaciones

La implementación actual realiza la conversión en memoria. No actualiza documentos directamente en Firestore ni ejecuta una migración masiva de la colección. Esto permite probar el comportamiento de manera controlada sin modificar datos existentes.

La estrategia conserva el contrato de validación de M05 y deja preparada una base para integrar posteriormente la evolución con el almacenamiento de documentos.

## 7. Conclusión

La implementación demuestra cómo evolucionar la estructura de los documentos de telemetría mediante versiones explícitas, validación reutilizada y pruebas automatizadas. De esta manera, se reducen los riesgos de aceptar datos inválidos o convertir documentos de una versión desconocida.


## Evolución compatible de documentos: v1 a v2

### Contexto

Los consumidores existentes utilizan documentos de telemetría en formato v1, con campos como `device_id`, `timestamp`, `metric`, `value` y `unit` en el nivel raíz. La versión v2 agrupa esos campos dentro de `reading` e incorpora `schema_version: 2`.

El objetivo es permitir la transición entre formatos sin impedir la lectura de documentos anteriores.

### Decisión

Se implementan tres operaciones:

- `read_telemetry_compatible(document)`: reconoce documentos v1 y v2, valida su estructura y devuelve los datos de telemetría en una representación común.
- `migrate_to_v2(document)`: convierte documentos v1 a v2 y acepta documentos v2 válidos. Repetir la migración sobre un documento ya migrado produce el mismo resultado normalizado.
- `rollback_to_v1(document)`: reconstruye la estructura de datos v1 a partir de un documento v2 válido.

Las operaciones trabajan sobre copias de los datos y no deben modificar el documento de entrada.

### Compatibilidad

Durante la transición, la lectura compatible admite ambas versiones. Los consumidores que necesiten los campos en el nivel raíz pueden utilizar la representación v1 reconstruida; los consumidores nuevos pueden utilizar el formato v2.

Los documentos con versiones desconocidas o datos que no cumplen la validación se rechazan explícitamente.

### Rollback y límites

El rollback reconstruye los campos de telemetría de v1, pero no constituye una reversión transaccional del almacén persistente. No restaura metadatos que se hayan descartado durante la migración ni revierte automáticamente escrituras en Firestore u otra base de datos.

La implementación actual proporciona conversión y lectura compatibles a nivel de documento. No ejecuta por sí sola una migración masiva ni modifica automáticamente los documentos almacenados.

### Verificación

Las pruebas automatizadas comprueban la migración de documentos válidos, el rechazo de datos inválidos y versiones desconocidas, la lectura compatible entre v1 y v2, la idempotencia de la migración y el rollback.

La última ejecución de `make verify` registró 51 pruebas aprobadas y 1 omitida. La prueba omitida corresponde a la integración real con Firestore, que requiere un servicio local disponible. Por ello, este resultado no demuestra por sí solo una migración persistente en Firestore.

### Consecuencias

La estrategia permite una transición gradual y facilita la compatibilidad entre consumidores antiguos y nuevos. Como contrapartida, los consumidores deben conocer el formato de los datos que reciben y la reversión persistente requiere un procedimiento adicional, respaldos y pruebas específicas.