# Reporte de Recuperación e Integración (M06)
**Responsable:** Integrante 3 (Erick)

## 1. Diseño de la Falla Controlada
Se simuló un escenario de pérdida de datos críticos mediante la eliminación directa de registros en el almacén documental (`DocumentStore`), confirmando la indisponibilidad de la información.

## 2. Recuperación y Fixture
Se inyectó un fixture válido (datos predefinidos de respaldo) para restaurar la operatividad del sistema a su estado previo a la falla.

## 3. Métricas de Recuperación
El tiempo de recuperación (restauración del fixture y disponibilidad de lectura) fue medido dinámicamente en las pruebas automatizadas, resultando en un promedio de **< 1 segundo**. Los registros recuperados mantuvieron el 100% de la integridad estructural.