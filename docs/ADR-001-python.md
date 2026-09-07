# ADR-001 — Elección del lenguaje de aplicación

## Estado

Aceptado

## Contexto

El proyecto CDRL requiere un lenguaje de aplicación para implementar la validación de los datos de telemetría y su integración con la base de datos PostgreSQL.

El lenguaje debe permitir implementar pruebas automatizadas, validación del contrato de datos y una integración reproducible con el entorno de base de datos.

## Decisión

El equipo selecciona **Python** como lenguaje de aplicación para el proyecto CDRL y, específicamente, para el hito M01.

Python se utilizará para:

* Implementar la lógica de validación del contrato de telemetría.
* Ejecutar las pruebas automatizadas.
* Integrarse con PostgreSQL.
* Ejecutar los scripts de preparación de la base de datos.
* Mantener una implementación sencilla y reproducible dentro del proyecto.

Para la integración con PostgreSQL se utilizará el controlador `psycopg`.

## Consecuencias

### Positivas

* Permite implementar rápidamente la lógica de validación.
* Facilita la creación de pruebas automatizadas con `pytest`.
* Cuenta con soporte para PostgreSQL mediante `psycopg`.
* Permite ejecutar los scripts del proyecto de forma reproducible.
* Mantiene una estructura sencilla para el desarrollo del hito M01.

### Negativas

* El equipo debe mantener una instalación compatible de Python en los entornos donde se ejecute el proyecto.
* Las dependencias de Python deben mantenerse documentadas en `requirements.txt`.

## Alternativas consideradas

### JavaScript / Node.js

Se consideró Node.js, pero el equipo decidió utilizar Python porque la validación y las pruebas requeridas para M01 pueden implementarse de forma sencilla con Python y `pytest`.

### Java

Se consideró Java, pero se descartó por requerir una estructura y configuración más extensa para las necesidades actuales del hito M01.

## Alcance

Esta decisión aplica al lenguaje de aplicación utilizado para M01 y puede revisarse en futuros hitos si cambian los requisitos del proyecto.
