

\# ADR-003: Seguridad y mínimo privilegio



\## Estado

Aceptado



\## Contexto

El sistema CDRL necesita controlar el acceso a la base de datos

para evitar que todos los usuarios tengan permisos administrativos.



\## Decisión

Se implementaron roles separados según la capacidad de cada usuario:



\- `cdrl\_migrator`: administración de migraciones.

\- `cdrl\_writer`: inserción y modificación de registros.

\- `cdrl\_reader`: consulta de registros.

\- `cdrl\_operator`: operaciones limitadas mediante permisos específicos.



Se crearon usuarios independientes con inicio de sesión y contraseñas

configuradas mediante variables de entorno, fuera del repositorio.



\## Permisos principales



| Rol | Permisos |

|---|---|

| Migrator | Privilegios de migración configurados |

| Writer | SELECT, INSERT, UPDATE |

| Reader | SELECT |

| Operator | Sin acceso directo a la tabla |



\## Validación

Se ejecutaron cinco pruebas de permisos:



\- Writer puede insertar: permitido.

\- Reader no puede insertar: denegado.

\- Reader no puede eliminar: denegado.

\- Writer no puede eliminar: denegado.

\- Operator no puede consultar la tabla: denegado.



Todas las pruebas obtuvieron el resultado esperado.



\## Rotación de contraseñas

Las contraseñas se administran mediante variables de entorno.

Para realizar una rotación, se actualiza la contraseña del usuario

en PostgreSQL y se modifica la variable de entorno correspondiente,

sin guardar credenciales en el repositorio.



\## Consecuencias

\- Se reduce el acceso innecesario a la base de datos.

\- Se separan las responsabilidades de cada usuario.

\- Se facilita la auditoría de permisos.

\- Las credenciales no se almacenan en el código fuente.

