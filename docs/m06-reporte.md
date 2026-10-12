# M06. Evolución documental, auditoría y recuperación

## 1. Objetivo

Demostrar la recuperación de documentos después de una falla controlada, comprobar la integridad de los datos restaurados y generar evidencia verificable de la operación.

## 2. Evolución de documentos

El proyecto cuenta con fixtures de documentos de las versiones 1 y 2 en la carpeta `fixtures/`. Estos archivos permiten representar la evolución del esquema documental y conservar ejemplos para las pruebas.

Archivos utilizados:
- `fixtures/m06-documents-v1.json`
- `fixtures/m06-documents-v2.json`

## 3. Falla controlada

La prueba elimina un documento de un almacén simulado en memoria y comprueba que ya no está disponible. Esta operación representa una pérdida controlada de información sin eliminar datos de un servicio externo.

## 4. Recuperación desde un fixture

Se restaura el documento utilizando los datos del fixture de la versión 1. Después se compara el documento recuperado con los datos originales para verificar que sus campos y valores se conservaron.

La prueba mide el tiempo de recuperación mediante `time.perf_counter()`. El resultado real se guarda en `artifacts/m06-recovery-results.json` al ejecutar la prueba correspondiente.

## 5. Casos de prueba

- Caso normal: eliminar y recuperar un documento desde el fixture.
- Caso límite 1: rechazar un documento vacío o inválido.
- Caso límite 2: comprobar que un documento inexistente no se devuelve como si estuviera recuperado.
- Fallo declarado: verificar que, si no se ejecuta la restauración, el documento continúa ausente.

## 6. Evidencias

La evidencia automatizada se genera en `artifacts/m06-recovery-results.json`. El reporte global de pruebas se encuentra en `artifacts/pytest-results.xml`, generado por el proceso de verificación del proyecto.

Los tiempos reportados deben proceder de una ejecución real; no se deben sustituir por valores estimados.

## 7. Limitaciones

La prueba de recuperación utiliza un almacén en memoria. Por lo tanto, valida el procedimiento de simulación y la integridad del fixture, pero no demuestra por sí sola la recuperación de una instancia real de Firestore o PostgreSQL.

## 8. Reproducción

Desde la raíz del repositorio, ejecutar:

```powershell
python -m pytest tests/test_recovery.py -v
make verify
```

En Windows, si `make` no está instalado, se debe ejecutar el verificador equivalente disponible en el proyecto.
