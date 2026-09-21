# Reporte de Gestión y Rotación de Secretos

## 1. Configuración Segura
Las credenciales de acceso a la base de datos se extrajeron del código y se gestionan a través de variables de entorno locales (archivo `.env`).

## 2. Revisión de Secretos Versionados
El archivo `.env` ha sido añadido a `.gitignore`. Se revisó el historial de commits y se confirma que no existen contraseñas, tokens ni secretos "hardcodeados" (quemados) en el repositorio.

## 3. Política de Rotación
* **Frecuencia:** Las contraseñas de PostgreSQL se rotarán cada 90 días o de inmediato si se sospecha de una brecha de seguridad.
* **Procedimiento:** 
  1. El administrador ejecutará el cambio de clave en la base de datos (`ALTER ROLE...`).
  2. Se notificará a los desarrolladores para actualizar su archivo `.env` local de manera segura.
  3. Se reiniciarán los contenedores de Docker (si aplica) para tomar la nueva configuración.