
# M08 â€“ PaginaciÃ³n, Ã­ndices y rendimiento

## 1. Objetivo

Implementar y evaluar estrategias de paginaciÃ³n para las lecturas de telemetrÃ­a, utilizando Ã­ndices y mediciones reproducibles de rendimiento.

## 2. ImplementaciÃ³n

Se implementÃ³ paginaciÃ³n por cursor (KEYSET) en PostgreSQL mediante el mÃ³dulo `src/database_pagination.py`.

La consulta utiliza los campos `timestamp` e `id` para mantener un orden descendente estable.

TambiÃ©n se incorporÃ³ el Ã­ndice compuesto:

`idx_telemetry_device_timestamp_id`

Este Ã­ndice utiliza las columnas:

- `device_id` ASC
- `timestamp` DESC
- `id` DESC

Se estableciÃ³ un tamaÃ±o de pÃ¡gina configurable entre 1 y 100 registros.

TambiÃ©n se implementÃ³ paginaciÃ³n por cursor para el almacÃ©n documental mediante los mÃ³dulos `src/document_pagination.py` y `src/document_store.py`.

## 3. Pruebas funcionales

Se realizaron pruebas unitarias para validar:

- CodificaciÃ³n y decodificaciÃ³n de cursores.
- Rechazo de cursores invÃ¡lidos.
- ValidaciÃ³n del tamaÃ±o de pÃ¡gina.
- Manejo de pÃ¡ginas consecutivas.
- Ausencia de identificadores duplicados.
- Orden descendente de los registros.

La prueba de integraciÃ³n con PostgreSQL utilizÃ³ siete registros sintÃ©ticos y verificÃ³ tres pÃ¡ginas consecutivas.

AdemÃ¡s, se insertÃ³ un registro mÃ¡s reciente despuÃ©s de consultar la primera pÃ¡gina. Al continuar con el cursor anterior, se comprobÃ³ que los siete registros originales se recuperaron sin duplicados y manteniendo el orden esperado.

Esta prueba comprueba el comportamiento ante una inserciÃ³n situada antes del cursor. No garantiza aislamiento de instantÃ¡nea: los registros nuevos que queden detrÃ¡s del cursor podrÃ­an aparecer en pÃ¡ginas posteriores.

## 4. Benchmark de rendimiento

Se compararon dos estrategias:

- OFFSET: paginaciÃ³n mediante desplazamiento.
- KEYSET: paginaciÃ³n mediante cursor.

### ConfiguraciÃ³n

- Motor: PostgreSQL 16.15.
- Registros sintÃ©ticos: 10,000.
- TamaÃ±o de pÃ¡gina: 50.
- Profundidad: posiciÃ³n 9,000.
- Calentamiento: 10 ejecuciones por estrategia.
- Muestras: 100 por estrategia.

### Resultados medidos

| MÃ©trica | OFFSET | KEYSET |
|---|---:|---:|
| p50 | 1.2636 ms | 0.4805 ms |
| p95 | 1.6806 ms | 0.8246 ms |
| MÃ­nimo | 1.1387 ms | 0.3940 ms |
| MÃ¡ximo | 2.3247 ms | 1.4894 ms |

KEYSET presentÃ³ una reducciÃ³n aproximada del 61.98 % en p50 y del 50.94 % en p95 frente a OFFSET en esta ejecuciÃ³n.

Ambas estrategias devolvieron exactamente los mismos registros durante la comprobaciÃ³n previa a las mediciones.

Los resultados detallados se guardaron en `artifacts/m08-benchmark-results.json`.

## 5. AnÃ¡lisis y tradeoffs

La paginaciÃ³n OFFSET es sencilla de implementar, pero necesita recorrer y descartar los registros anteriores al desplazamiento solicitado.

KEYSET utiliza los valores de la Ãºltima lectura como referencia para continuar la consulta. Esto evita recorrer todos los registros anteriores a la pÃ¡gina solicitada y resulta conveniente para recorridos secuenciales profundos.

Como tradeoff, KEYSET requiere mantener y validar un cursor entre solicitudes. AdemÃ¡s, no representa una fotografÃ­a inmutable de toda la tabla: las inserciones y eliminaciones concurrentes pueden afectar quÃ© registros aparecen durante el recorrido.

## 6. Limitaciones

Las mediciones corresponden a PostgreSQL local y a un conjunto de datos sintÃ©ticos controlado. Los tiempos dependen del hardware, la configuraciÃ³n y la carga del entorno.

Los resultados corresponden Ãºnicamente a PostgreSQL y no representan mediciones de Firestore.

La prueba de integraciÃ³n real de Firestore permanece omitida cuando no estÃ¡ disponible un emulador local.

## 7. ConclusiÃ³n

La implementaciÃ³n de paginaciÃ³n KEYSET funcionÃ³ correctamente en PostgreSQL y presentÃ³ menor latencia p50 y p95 que OFFSET durante el benchmark realizado.

Las pruebas confirmaron la validaciÃ³n de cursores, el orden estable de los registros, la ausencia de duplicados y el comportamiento ante una inserciÃ³n mÃ¡s reciente entre pÃ¡ginas.

En el entorno evaluado, KEYSET resultÃ³ conveniente para consultar pÃ¡ginas profundas. Sin embargo, los resultados no deben generalizarse a otros motores o entornos sin realizar nuevas mediciones.

La evidencia de pruebas, configuraciÃ³n y resultados se conserva en los archivos correspondientes de `artifacts/` y `evidence/`.
