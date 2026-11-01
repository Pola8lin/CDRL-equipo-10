# M08 – Paginación, índices y rendimiento

## 1. Objetivo
Implementar y evaluar estrategias de paginación para las lecturas de telemetría, utilizando índices y mediciones reproducibles de rendimiento.

## 2. Implementación
Se implementó paginación por cursor (KEYSET) en PostgreSQL mediante el módulo `src/database_pagination.py`.

La consulta utiliza los campos `timestamp` e `id` para mantener un orden descendente estable.

También se incorporó el índice compuesto:
`idx_telemetry_device_timestamp_id`

Este índice utiliza las columnas:
- `device_id` ASC
- `timestamp` DESC
- `id` DESC

Se estableció un tamaño de página configurable entre 1 y 100 registros.

También se implementó paginación por cursor para el almacén documental mediante los módulos `src/document_pagination.py` y `src/document_store.py`.

## 3. Pruebas funcionales
Se realizaron pruebas unitarias para validar:
- Codificación y decodificación de cursores.
- Rechazo de cursores inválidos.
- Validación del tamaño de página.
- Manejo de páginas consecutivas.
- Ausencia de identificadores duplicados.
- Orden descendente de los registros.

La prueba de integración con PostgreSQL utilizó siete registros sintéticos y verificó tres páginas consecutivas.

Además, se insertó un registro más reciente después de consultar la primera página. Al continuar con el cursor anterior, se comprobó que los siete registros originales se recuperaron sin duplicados y manteniendo el orden esperado.

Esta prueba comprueba el comportamiento ante una inserción situada antes del cursor. No garantiza aislamiento de instantánea: los registros nuevos que queden detrás del cursor podrían aparecer en páginas posteriores.

## 4. Benchmark de rendimiento
Se compararon dos estrategias:
- OFFSET: paginación mediante desplazamiento.
- KEYSET: paginación mediante cursor.

### Configuración
- Motor: PostgreSQL 16.15.
- Registros sintéticos: 10,000.
- Tamaño de página: 50.
- Profundidad: posición 9,000.
- Calentamiento: 10 ejecuciones por estrategia.
- Muestras: 100 por estrategia.

### Resultados medidos

| Métrica | OFFSET | KEYSET |
|---|---:|---:|
| p50 | 1.2636 ms | 0.4805 ms |
| p95 | 1.6806 ms | 0.8246 ms |
| Mínimo | 1.1387 ms | 0.3940 ms |
| Máximo | 2.3247 ms | 1.4894 ms |

KEYSET presentó una reducción aproximada del 61.98 % en p50 y del 50.94 % en p95 frente a OFFSET en esta ejecución.

Ambas estrategias devolvieron exactamente los mismos registros durante la comprobación previa a las mediciones.

Los resultados detallados se guardaron en `artifacts/m08-benchmark-results.json`.

## 5. Análisis y tradeoffs
La paginación OFFSET es sencilla de implementar, pero necesita recorrer y descartar los registros anteriores al desplazamiento solicitado.

KEYSET utiliza los valores de la última lectura como referencia para continuar la consulta. Esto evita recorrer todos los registros anteriores a la página solicitada y resulta conveniente para recorridos secuenciales profundos.

Como tradeoff, KEYSET requiere mantener y validar un cursor entre solicitudes. Además, no representa una fotografía inmutable de toda la tabla: las inserciones y eliminaciones concurrentes pueden afectar qué registros aparecen durante el recorrido.

## 6. Limitaciones
Las mediciones corresponden a PostgreSQL local y a un conjunto de datos sintéticos controlado. Los tiempos dependen del hardware, la configuración y la carga del entorno.

Los resultados corresponden únicamente a PostgreSQL y no representan mediciones de Firestore.

## 7. Conclusión
La implementación de paginación KEYSET funcionó correctamente en PostgreSQL y presentó menor latencia p50 y p95 que OFFSET durante el benchmark realizado.

Las pruebas confirmaron la validación de cursores, el orden estable de los registros, la ausencia de duplicados y el comportamiento ante una inserción más reciente entre páginas.

En el entorno evaluado, KEYSET resultó conveniente para consultar páginas profundas. Sin embargo, los resultados no deben generalizarse a otros motores o entornos sin realizar nuevas mediciones.

La evidencia de pruebas, configuración y resultados se conserva en los archivos correspondientes de `artifacts/` y `evidence/`.