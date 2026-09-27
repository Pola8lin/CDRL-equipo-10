# ADR-004: Decisión Arquitectónica NoSQL para Eventos de Telemetría

## Estado
Aceptado

## Contexto y Problema
El sistema CDRL procesa eventos de telemetría de manera continua. Cada evento contiene: `device_id`, `timestamp`, `metric`, `value` y `unit`. Si bien la base de datos relacional actual funciona, el aumento proyectado en la cantidad de dispositivos requiere evaluar e integrar un almacenamiento NoSQL especializado que permita manejar grandes volúmenes de datos con un enfoque específico en escalabilidad temporal, sin comprometer el rendimiento general del sistema.

## Opciones Consideradas
Según la matriz de decisión (M04), se evaluaron las siguientes alternativas para complementar el sistema:
1. **Document Store:** Firebase Cloud Firestore
2. **Graph Store:** Neo4j
3. **Wide-Column Store:** Apache Cassandra
4. **Object Store:** Amazon S3

## Decisión
Se ha decidido utilizar **Firebase Cloud Firestore (Document Store)** como la base de datos NoSQL oficial para el registro de los eventos de telemetría de CDRL, habiendo obtenido la mayor puntuación en la matriz de evaluación técnica (89/100).

## Justificación Arquitectónica (Conexión con Criterios)
La elección de Firestore impacta y satisface directamente los 5 criterios evaluados:

* **Consultas:** El modelo orientado a documentos permite almacenar el evento tal cual se genera y facilita directamente nuestro principal patrón de consulta operacional: filtrar y buscar por `device_id` y por rangos de `timestamp`.
* **Escala:** Al ser un servicio administrado (Serverless), Firestore escalará automáticamente conforme aumente el volumen de dispositivos (1K, 10K, 100K eventos) sin que el equipo requiera administrar los nodos subyacentes.
* **Consistencia:** Proporciona operaciones atómicas y fuertes mecanismos transaccionales, garantizando que los datos escritos coincidan exactamente con las lecturas posteriores.
* **Costo y Operación:** Se reduce drásticamente el esfuerzo de operación de infraestructura al no requerir mantenimiento, balanceo ni parches de SO. El modelo de costos se basará estrictamente en el uso por operaciones de lectura/escritura.
* **Tolerancia a fallos:** El servicio proporciona alta disponibilidad, redundancia y durabilidad de manera administrada y nativa.

## Alternativa Descartada
**PostgreSQL como única solución:** 
Aunque PostgreSQL es capaz de manejar el volumen actual (y se mantendrá para la gestión de usuarios), se descarta utilizarlo como la *única* solución de almacenamiento total. A largo plazo, el volumen masivo de telemetría obligaría a implementar un particionamiento complejo, indexación exhaustiva y estrategias manuales de archivado. Se descarta para eventos masivos a favor de una solución NoSQL especializada.

## Consecuencias
* Reducción del esfuerzo de DevOps y mantenimiento de servidores.
* Necesidad de adaptar el modelo de datos para optimizar los costos, limitando lecturas innecesarias.
* Arquitectura híbrida: Firestore para la alta ingesta de telemetría temporal y PostgreSQL para el modelo relacional.

## Diagrama de Arquitectura Híbrida

```text
[Dispositivos CDRL] 
       │
       ▼
 [API / Ingesta] ─── (Datos Relacionales/Seguridad) ───> [PostgreSQL]
       │
       └─── (Eventos masivos de telemetría) ───────────> [Firebase Cloud Firestore]