# M04 — Matriz de decisión NoSQL

## 1. Objetivo

El objetivo de esta actividad es comparar diferentes modelos de almacenamiento NoSQL para determinar cuál se adapta mejor al manejo de eventos y telemetría del proyecto CDRL.

Se evaluaron cuatro alternativas:

1. **Document Store:** Firebase Cloud Firestore
2. **Graph Store:** Neo4j
3. **Wide-Column Store:** Apache Cassandra
4. **Object Store:** Amazon S3

La comparación considera cinco criterios relacionados directamente con las necesidades del sistema:

* Consultas
* Escalabilidad
* Consistencia
* Costo y operación
* Tolerancia a fallos

La matriz utiliza una escala de 1 a 5 y una ponderación que representa la importancia relativa de cada criterio.

---

## 2. Datos que maneja CDRL

Los eventos de telemetría utilizados para la comparación contienen los siguientes campos:

| Campo       | Descripción                                        |
| ----------- | -------------------------------------------------- |
| `device_id` | Identificador del dispositivo que generó el evento |
| `timestamp` | Fecha y hora en la que se produjo la lectura       |
| `metric`    | Tipo de métrica registrada                         |
| `value`     | Valor numérico de la medición                      |
| `unit`      | Unidad de medida                                   |

### Ejemplo de evento

```json
{
  "device_id": "sensor-001",
  "timestamp": "2026-09-26T10:30:00Z",
  "metric": "temperature",
  "value": 25.40,
  "unit": "°C"
}
```

Estos datos presentan un patrón principalmente temporal: un mismo dispositivo puede generar numerosos eventos a lo largo del tiempo.

Por esta razón, una de las consultas importantes para la evaluación es obtener los eventos de un dispositivo dentro de un rango de tiempo.

---

## 3. Alternativas consideradas

### 3.1 Firebase Cloud Firestore

Firebase Cloud Firestore es una base de datos NoSQL orientada a documentos. Los datos se organizan mediante colecciones y documentos, permitiendo almacenar información estructurada y objetos anidados.

Para CDRL, un evento de telemetría puede representarse directamente como un documento que contenga `device_id`, `timestamp`, `metric`, `value` y `unit`.

Firestore permite realizar consultas mediante filtros, ordenamiento, límites y cursores. Esto permite plantear consultas como:

* Obtener eventos de un dispositivo.
* Obtener eventos de un dispositivo dentro de un rango de tiempo.
* Filtrar por dispositivo y métrica.
* Ordenar los eventos por fecha.

También proporciona mecanismos transaccionales y servicios administrados, por lo que la infraestructura subyacente no necesita ser administrada directamente por el equipo.

El costo depende del uso de operaciones, almacenamiento e índices, por lo que debe analizarse de acuerdo con el volumen y patrón de consultas del sistema.

**Hipótesis asociada:** Firestore puede almacenar y consultar los eventos de CDRL mediante `device_id` y `timestamp` de manera directa.

---

### 3.2 Neo4j

Neo4j es una base de datos orientada a grafos. Su modelo representa información mediante nodos, relaciones y propiedades.

En el escenario CDRL, un modelo de ejemplo podría representar:

```text
Dispositivo
    │
    ├── genera ──> Evento
    │                │
    │                └── corresponde a ──> Métrica
    │
    └── pertenece a ──> Ubicación
```

Este modelo puede ser útil si el sistema necesita consultar relaciones entre dispositivos, eventos, ubicaciones, métricas u otras entidades.

Neo4j utiliza Cypher para expresar consultas sobre patrones y relaciones del grafo.

Sin embargo, las consultas básicas de telemetría que solamente requieren buscar eventos por dispositivo y tiempo no dependen necesariamente de relaciones complejas.

**Hipótesis asociada:** Neo4j puede proporcionar ventajas cuando las consultas requieren recorrer relaciones entre entidades, mientras que las consultas simples de dispositivo y tiempo no explotan completamente el modelo de grafos.

---

### 3.3 Apache Cassandra

Apache Cassandra es una base de datos NoSQL distribuida de tipo wide-column, diseñada para trabajar con grandes cantidades de información y distribuir los datos entre diferentes nodos.

En CDRL, el diseño puede considerar `device_id` como parte principal de la estrategia de particionamiento y `timestamp` como elemento utilizado para organizar las lecturas temporales.

Una consulta representativa sería:

```text
Obtener los eventos de sensor-001
entre 2026-09-26T10:00:00Z
y 2026-09-26T11:00:00Z
```

Cassandra está orientada a escenarios donde se requiere distribuir grandes volúmenes de datos y mantener operaciones mediante múltiples nodos.

Una característica importante es que sus garantías de consistencia pueden configurarse mediante diferentes niveles de consistencia. Por lo tanto, no debe considerarse simplemente como una solución "sin consistencia".

Su principal consideración para este proyecto es el esfuerzo de operación y administración de una infraestructura distribuida, especialmente frente a una solución administrada.

**Hipótesis asociada:** las ventajas de Cassandra serán más evidentes conforme aumenten el volumen de eventos y la carga de escritura y consulta.

---

### 3.4 Amazon S3

Amazon S3 es un servicio de almacenamiento de objetos. A diferencia de una base de datos operacional, organiza la información como objetos dentro de buckets.

Para CDRL podría utilizarse para almacenar:

* Archivos históricos de telemetría.
* Exportaciones de eventos.
* Respaldos.
* Archivos JSON.
* Datos destinados a procesos posteriores de análisis.

Un ejemplo conceptual sería:

```text
bucket/
├── telemetry/
│   ├── 2026/
│   │   ├── 09/
│   │   │   ├── 26/
│   │   │   │   ├── sensor-001.json
│   │   │   │   └── sensor-002.json
```

S3 está diseñado para almacenar grandes cantidades de objetos y proporciona mecanismos de redundancia y durabilidad.

Sin embargo, realizar consultas operacionales frecuentes sobre eventos individuales o rangos temporales no es su función principal. Para escenarios analíticos o consultas sobre grandes cantidades de objetos pueden ser necesarios servicios adicionales.

**Hipótesis asociada:** S3 será más adecuado para conservación histórica, respaldos y almacenamiento de archivos que para consultas operacionales frecuentes de telemetría.

---

## 4. Criterios de evaluación

Para realizar la comparación se definieron cinco criterios.

| Criterio            |     Peso | Justificación                                                                |
| ------------------- | -------: | ---------------------------------------------------------------------------- |
| Consultas           |      25% | El sistema necesita consultar eventos por dispositivo y tiempo.              |
| Escalabilidad       |      25% | El número de eventos puede aumentar conforme se incorporen más dispositivos. |
| Consistencia        |      20% | Los eventos almacenados deben conservar sus valores correctamente.           |
| Costo y operación   |      15% | Se debe considerar el esfuerzo necesario para mantener la solución.          |
| Tolerancia a fallos |      15% | La solución debe contemplar fallos de componentes o infraestructura.         |
| **Total**           | **100%** |                                                                              |

### Escala utilizada

| Puntuación | Interpretación   |
| ---------: | ---------------- |
|          1 | Muy desfavorable |
|          2 | Desfavorable     |
|          3 | Aceptable        |
|          4 | Favorable        |
|          5 | Muy favorable    |

La puntuación representa qué tan bien cada alternativa se adapta específicamente al escenario evaluado. No representa una clasificación universal de las tecnologías.

---

## 5. Fórmula de ponderación

Para cada criterio se utiliza la siguiente fórmula:

```text
Puntuación ponderada = (Puntuación / 5) × Peso
```

Por ejemplo, si una alternativa obtiene una puntuación de 4 en un criterio cuyo peso es 25%:

```text
(4 / 5) × 25 = 20
```

La puntuación final corresponde a la suma de las puntuaciones ponderadas de los cinco criterios.

---

## 6. Matriz de decisión

| Alternativa              | Consultas 25% | Escalabilidad 25% | Consistencia 20% | Costo/Operación 15% | Fallos 15% | Total / 100 |
| ------------------------ | ------------: | ----------------: | ---------------: | ------------------: | ---------: | ----------: |
| Firebase Cloud Firestore |             5 |                 4 |                5 |                   4 |          4 |      **89** |
| Neo4j                    |             3 |                 4 |                5 |                   3 |          4 |      **76** |
| Apache Cassandra         |             5 |                 5 |                3 |                   3 |          5 |      **86** |
| Amazon S3                |             2 |                 5 |                5 |                   5 |          5 |      **85** |

### Cálculo de Firebase Cloud Firestore

```text
Consultas:
(5 / 5) × 25 = 25

Escalabilidad:
(4 / 5) × 25 = 20

Consistencia:
(5 / 5) × 20 = 20

Costo/Operación:
(4 / 5) × 15 = 12

Tolerancia a fallos:
(4 / 5) × 15 = 12

Total:
25 + 20 + 20 + 12 + 12 = 89
```

### Cálculo de Neo4j

```text
Consultas:
(3 / 5) × 25 = 15

Escalabilidad:
(4 / 5) × 25 = 20

Consistencia:
(5 / 5) × 20 = 20

Costo/Operación:
(3 / 5) × 15 = 9

Tolerancia a fallos:
(4 / 5) × 15 = 12

Total:
15 + 20 + 20 + 9 + 12 = 76
```

### Cálculo de Apache Cassandra

```text
Consultas:
(5 / 5) × 25 = 25

Escalabilidad:
(5 / 5) × 25 = 25

Consistencia:
(3 / 5) × 20 = 12

Costo/Operación:
(3 / 5) × 15 = 9

Tolerancia a fallos:
(5 / 5) × 15 = 15

Total:
25 + 25 + 12 + 9 + 15 = 86
```

### Cálculo de Amazon S3

```text
Consultas:
(2 / 5) × 25 = 10

Escalabilidad:
(5 / 5) × 25 = 25

Consistencia:
(5 / 5) × 20 = 20

Costo/Operación:
(5 / 5) × 15 = 15

Tolerancia a fallos:
(5 / 5) × 15 = 15

Total:
10 + 25 + 20 + 15 + 15 = 85
```

---

## 7. Justificación de las puntuaciones

### Firebase Cloud Firestore

**Consultas — 5/5**

El modelo de documentos permite representar directamente los eventos de CDRL y realizar consultas utilizando campos como `device_id`, `timestamp` y `metric`.

**Escalabilidad — 4/5**

Al ser un servicio administrado, puede manejar incrementos de carga sin que el equipo tenga que administrar manualmente los servidores subyacentes.

**Consistencia — 5/5**

Firestore proporciona operaciones atómicas y mecanismos transaccionales para determinados escenarios.

**Costo y operación — 4/5**

La administración de infraestructura es reducida porque se trata de un servicio administrado. Sin embargo, el costo depende del uso, almacenamiento e índices.

**Tolerancia a fallos — 4/5**

El servicio está diseñado para proporcionar disponibilidad y redundancia según la configuración y edición utilizada.

---

### Neo4j

**Consultas — 3/5**

Es especialmente adecuado para consultas que recorren relaciones. Sin embargo, las consultas principales del escenario CDRL son principalmente temporales y por dispositivo.

**Escalabilidad — 4/5**

Puede utilizar arquitecturas distribuidas dependiendo de la edición y configuración utilizada.

**Consistencia — 5/5**

Su modelo transaccional permite trabajar con operaciones consistentes sobre los datos.

**Costo y operación — 3/5**

Puede requerir mayor conocimiento y administración de infraestructura que una solución completamente administrada.

**Tolerancia a fallos — 4/5**

Puede utilizar mecanismos de replicación y arquitecturas distribuidas dependiendo de la configuración.

---

### Apache Cassandra

**Consultas — 5/5**

Su diseño basado en particiones puede adaptarse a consultas de eventos por dispositivo y rango temporal cuando el modelo de datos se diseña específicamente para esos patrones.

**Escalabilidad — 5/5**

Está diseñada para distribuir grandes volúmenes de datos y cargas de trabajo entre múltiples nodos.

**Consistencia — 3/5**

Cassandra ofrece niveles de consistencia configurables. Esto proporciona flexibilidad, pero requiere diseñar y seleccionar correctamente las garantías necesarias para cada operación.

**Costo y operación — 3/5**

Una implementación propia implica administrar nodos, configuración, monitoreo, almacenamiento y mantenimiento.

**Tolerancia a fallos — 5/5**

Su arquitectura distribuida y mecanismos de replicación permiten continuar las operaciones ante determinados fallos, dependiendo de la configuración.

---

### Amazon S3

**Consultas — 2/5**

S3 es almacenamiento de objetos y no una base de datos operacional de eventos. Las consultas frecuentes por dispositivo y rango de tiempo pueden requerir procesamiento o servicios adicionales.

**Escalabilidad — 5/5**

Está diseñado para almacenar grandes cantidades de objetos.

**Consistencia — 5/5**

S3 proporciona consistencia fuerte para las operaciones de lectura después de escritura y eliminación de objetos.

**Costo y operación — 5/5**

La administración de servidores es mínima porque se trata de almacenamiento administrado. El costo económico real depende del almacenamiento, solicitudes, transferencia y otros factores de uso.

**Tolerancia a fallos — 5/5**

El servicio utiliza mecanismos de redundancia y está diseñado para proporcionar alta durabilidad de los objetos almacenados.

---

## 8. Hipótesis falsables

La matriz no se basa únicamente en opiniones. Cada criterio se relaciona con una hipótesis que puede comprobarse mediante pruebas o evidencia documental.

### H1 — Consultas

**Hipótesis:**

> Las alternativas evaluadas pueden almacenar los eventos de CDRL, pero su capacidad para realizar consultas operacionales por dispositivo y rango de tiempo será diferente según el modelo de almacenamiento.

**Prueba propuesta:**

Utilizar eventos sintéticos y ejecutar consultas para:

```text
1. device_id = sensor-001
2. device_id + rango de timestamp
3. device_id + metric + timestamp
```

**Criterio de confirmación:**

La hipótesis se confirma si las alternativas permiten realizar las consultas requeridas y las diferencias observadas corresponden a las características documentadas de cada modelo.

**Criterio de rechazo:**

Se rechaza si una alternativa no puede realizar correctamente una consulta requerida o necesita una transformación incompatible con el escenario evaluado.

---

### H2 — Escalabilidad

**Hipótesis:**

> Las alternativas distribuidas o administradas podrán mantener las operaciones de almacenamiento y consulta conforme aumente el volumen de eventos sintéticos de CDRL, aunque su comportamiento y esfuerzo operativo serán diferentes.

**Prueba propuesta:**

Utilizar diferentes cantidades de eventos:

```text
1,000
10,000
100,000
1,000,000
```

Registrar:

* Tiempo de escritura.
* Tiempo de consulta.
* Errores.
* Recursos utilizados.
* Comportamiento al incrementar el volumen.

**Criterio de confirmación:**

La hipótesis se confirma si las operaciones continúan funcionando conforme aumenta el volumen y el comportamiento observado coincide con las características esperadas de cada alternativa.

**Criterio de rechazo:**

Se rechaza si una alternativa deja de soportar las operaciones necesarias o presenta un crecimiento de recursos incompatible con el escenario.

---

### H3 — Consistencia

**Hipótesis:**

> Las alternativas evaluadas proporcionarán mecanismos suficientes para mantener la integridad de los eventos de CDRL, aunque las garantías y mecanismos de consistencia serán diferentes entre los modelos.

**Prueba propuesta:**

Realizar:

```text
INSERT → READ → UPDATE → READ
```

y comprobar:

```text
device_id
timestamp
metric
value
unit
```

También se puede evaluar el comportamiento de operaciones concurrentes cuando la tecnología lo permita.

**Criterio de confirmación:**

La hipótesis se confirma si las lecturas corresponden con los valores escritos y el comportamiento observado respeta las garantías documentadas.

**Criterio de rechazo:**

Se rechaza si los resultados contradicen las garantías de consistencia configuradas o documentadas.

---

### H4 — Costo y operación

**Hipótesis:**

> Las soluciones administradas requerirán menor esfuerzo de operación directa que las soluciones que requieren administrar infraestructura propia, aunque el costo económico dependerá del volumen y patrón de uso.

**Prueba propuesta:**

Documentar las tareas necesarias para cada alternativa:

* Instalación.
* Configuración.
* Actualizaciones.
* Escalamiento.
* Monitoreo.
* Recuperación ante fallos.
* Administración de infraestructura.
* Modelo general de costos.

**Criterio de confirmación:**

La hipótesis se confirma si las soluciones administradas requieren menos tareas de infraestructura directa.

**Criterio de rechazo:**

Se rechaza si una alternativa administrada requiere prácticamente el mismo nivel de administración directa que una solución autogestionada en el escenario utilizado.

---

### H5 — Tolerancia a fallos

**Hipótesis:**

> Las arquitecturas que utilizan redundancia y replicación podrán mantener los datos disponibles ante determinados fallos de infraestructura, dependiendo de su configuración.

**Prueba propuesta:**

Cuando la implementación lo permita, realizar un fallo controlado de un componente o nodo y comprobar:

```text
1. Disponibilidad de lectura.
2. Disponibilidad de escritura.
3. Integridad de los datos.
4. Recuperación después del fallo.
```

**Criterio de confirmación:**

La hipótesis se confirma si la operación continúa o se recupera de acuerdo con la configuración y garantías documentadas.

**Criterio de rechazo:**

Se rechaza si el fallo provoca pérdida de datos o indisponibilidad contraria a las garantías configuradas.

---

## 9. Resumen de hipótesis y evidencia

| ID | Criterio            | Hipótesis                                                                                | Evidencia                                            |
| -- | ------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| H1 | Consultas           | Las alternativas presentan diferentes capacidades para consultas operacionales.          | Consultas sobre fixtures sintéticos.                 |
| H2 | Escalabilidad       | El comportamiento cambia conforme aumenta el volumen de eventos.                         | Pruebas con 1K, 10K, 100K y 1M eventos.              |
| H3 | Consistencia        | Las alternativas ofrecen diferentes mecanismos y garantías de consistencia.              | INSERT, READ, UPDATE y comprobación de resultados.   |
| H4 | Costo/Operación     | Las soluciones administradas reducen la administración directa de infraestructura.       | Comparación de tareas operativas y modelo de costos. |
| H5 | Tolerancia a fallos | La redundancia y replicación pueden mantener la disponibilidad ante determinados fallos. | Prueba controlada de fallo y recuperación.           |

---

## 10. Alternativa descartada

### PostgreSQL como única solución

PostgreSQL se considera una alternativa válida para el escenario actual y no se descarta por falta de capacidad.

La razón para considerarlo como alternativa descartada dentro de esta decisión arquitectónica es que el objetivo de M04 es evaluar modelos NoSQL para complementar o atender necesidades futuras relacionadas con grandes volúmenes de eventos.

**Hipótesis de descarte:**

> PostgreSQL como única solución puede continuar atendiendo el volumen actual de CDRL, pero ante un crecimiento considerable del volumen de telemetría podría requerir estrategias adicionales de particionamiento, indexación, retención, archivado, replicación o escalamiento.

Por lo tanto, el descarte no significa que PostgreSQL sea inadecuado, sino que se considera necesario evaluar modelos especializados para determinados patrones de crecimiento y almacenamiento.

La evidencia deberá obtenerse mediante pruebas de carga, mediciones del comportamiento del sistema y comparación con las características de las alternativas NoSQL.

---

## 11. Resultado de la matriz

Los resultados de la matriz son:

```text
Firebase Cloud Firestore = 89
Apache Cassandra         = 86
Amazon S3                = 85
Neo4j                    = 76
```

Estos valores representan la evaluación preliminar para el escenario específico de CDRL y deben interpretarse junto con las hipótesis y las pruebas propuestas.

La matriz no pretende establecer una clasificación universal de las tecnologías. Su propósito es documentar de forma reproducible los criterios utilizados para la decisión arquitectónica.

---

## 12. Evidencia esperada

Para validar la matriz se propone generar evidencia mediante:

1. Fixtures sintéticos de eventos CDRL.
2. Consultas por `device_id`.
3. Consultas por rango de `timestamp`.
4. Pruebas de incremento de volumen.
5. Pruebas de lectura y escritura.
6. Evaluación de mecanismos de consistencia.
7. Comparación de tareas de operación.
8. Pruebas controladas de fallos cuando la arquitectura utilizada lo permita.

Los resultados obtenidos deberán registrarse posteriormente en:

```text
evidence/m04-nosql-decision.json
```

y los datos estructurados de esta matriz deberán mantenerse en:

```text
artifacts/m04-decision-matrix.json
```

---

## 13. Referencias

* Firebase Documentation — Cloud Firestore.
* Neo4j Documentation — Graph Database y Cypher.
* Apache Cassandra Documentation.
* Amazon Web Services Documentation — Amazon S3.

Las referencias deberán conservarse junto con la documentación del ADR para que las afirmaciones técnicas puedan verificarse.