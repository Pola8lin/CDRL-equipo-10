\# M07 — Evolución compatible de documentos



\## Objetivo



Implementar versionado y migración compatible de documentos sin romper consumidores existentes.



\## Implementación



El módulo `src/document\_evolution.py` implementa:



\- `read\_telemetry\_compatible(document)`: permite leer documentos v1 y v2.

\- `migrate\_to\_v2(document)`: convierte documentos v1 a v2 y permite repetir la migración de forma idempotente.

\- `rollback\_to\_v1(document)`: reconstruye la estructura anterior a partir de un documento v2 válido.



La validación de los datos reutiliza las reglas existentes. Las versiones desconocidas y los documentos inválidos se rechazan.



\## Pruebas



El archivo `tests/test\_document\_evolution.py` incluye pruebas de migración, compatibilidad, idempotencia, validación y rollback.



La ejecución de `make verify` del 25 de octubre de 2026 terminó con:



\- 51 pruebas aprobadas.

\- 0 pruebas fallidas.

\- 1 prueba omitida.

\- Duración: 1.35 segundos.



La prueba omitida corresponde a la integración real con Firestore, que requiere un servicio local disponible.



\## Compatibilidad y límites



La lectura compatible permite trabajar con documentos v1 y v2 durante la transición. La migración se realiza a nivel de documento en memoria; no implica una actualización masiva del almacén persistente.



El rollback reconstruye la estructura v1, pero no revierte transacciones ni escrituras efectuadas en una base de datos. Una migración persistente requiere un procedimiento adicional y pruebas específicas.



\## Evidencia



\- `artifacts/pytest-results.xml`

\- `artifacts/m07-compatible-evolution-results.json`

\- `evidence/m07-compatible-evolution.json`



\## Conclusión



La implementación y las pruebas respaldan la lectura compatible, la migración repetible y el rollback a nivel de documento. La integración persistente con Firestore permanece fuera de lo demostrado por esta ejecución.
