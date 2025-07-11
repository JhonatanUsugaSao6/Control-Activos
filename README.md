# Sistema de Control Activos

Este sistema permite gestionar las salidas de los activos de la empresa, eliminando la dependencia de registros físicos y mejorando la trazabilidad de la información.

## Características principales
- **Salida manual**: Se ingresa el número del documento manual, se verifica si los campos están correctos y se adjunta una foto del documento.
- **Salida por llantas o TRI**: Se ingresa el número de consecutivo, el sistema carga automáticamente los datos relacionados y se valida la información antes de guardar.

## Arquitectura del Sistema
El sistema está desarrollado con el framework **Django** siguiendo el patrón **Model-Template-View (MTV)**:
- **Modelos**: Representan la estructura de la base de datos mediante el ORM de Django.
- **Vistas**: Gestionan la lógica del negocio y la interacción con los modelos.
- **Plantillas**: Manejan la presentación con HTML, CSS y Bootstrap.

## Tecnologías utilizadas
- **Backend**: Django 5.1.5, Django Templates, Django ORM, Asgiref 3.8.1, sqlparse 0.5.3
- **Frontend**: Bootstrap, HTML5, CSS3, JavaScript, AJAX
- **Base de Datos**: MySQL con mysqlclient y pyodbc
- **Seguridad**: Middleware de Django, autenticación y protección CSRF
- **Manejo de archivos**: Configuración de archivos estáticos y multimedia con Pillow y tzdata

## Estructura del Proyecto
El proyecto se organiza en carpetas siguiendo la estructura de Django:
```
ControlActivos/
│── Public/
    │── css/
    │── img/
    │── js/
│── Templates/
    │── Inc/
    │── Login/
    │── Tri/
│── __init__.py
│── asgi.py
│── forms.py
│── models.py
│── settings.py
│── urls.py
│── views.py
│── wsgi.py
│── env/
│── media/
│── README.md
│── manage.py
│── requirements.txt
```

## Base de Datos
El sistema gestiona los registros de las salidas mediante las siguientes tablas principales:
- `validacion_manual`: Almacena información sobre las salidas de los activos por medio del tipo manual.
- `validacion_tri`: Almacena información sobre las salidas de los activos por medio del tipo tri.
- `validacion_manual`: Almacena información sobre las salidas de los activos por medio del tipo llantas.

### Creación de la Base de Datos
```sql
CREATE DATABASE controlactivos;

USE controlactivos;

CREATE TABLE `validacion_tri` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `consecutivo` varchar(15) NOT NULL,
  `referencia` varchar(15) NOT NULL,
  `descripcion` varchar(100) NOT NULL,
  `bodega` varchar(100) NOT NULL,
  `extension` varchar(100) NOT NULL,
  `unidad_medida` varchar(15) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `ubicacion` varchar(100) NOT NULL,
  `validacion_descripcion` varchar(50) DEFAULT NULL,
  `validacion_cantidad` varchar(50) DEFAULT NULL,
  `validacion_proveedor` varchar(50) DEFAULT NULL,
  `validacion_marcacion` varchar(50) DEFAULT NULL,
  `validacion_fecha_tri` varchar(50) DEFAULT NULL,
  `validacion_sello` varchar(50) DEFAULT NULL,
  `validacion_firma_almacen` varchar(50) DEFAULT NULL,
  `validacion_firma_proveedor` varchar(50) DEFAULT NULL,
  `vigilante_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vigilante_id` (`vigilante_id`),
  CONSTRAINT `validacion_tri_ibfk_1` FOREIGN KEY (`vigilante_id`) REFERENCES `auth_user` (`id`)
) 

CREATE TABLE `validacion_llantas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `consecutivo` varchar(15) NOT NULL,
  `referencia` varchar(15) NOT NULL,
  `descripcion` varchar(100) NOT NULL,
  `bodega` varchar(100) NOT NULL,
  `extension` varchar(100) NOT NULL,
  `ubicacion` varchar(100) NOT NULL,
  `serial` varchar(100) NOT NULL,
  `quemado` varchar(100) NOT NULL,
  `vin` varchar(100) NOT NULL,
  `validacion_descripcion` varchar(50) DEFAULT NULL,
  `validacion_serial` varchar(50) DEFAULT NULL,
  `validacion_quemado` varchar(50) DEFAULT NULL,
  `validacion_vin` varchar(50) DEFAULT NULL,
  `validacion_proveedor` varchar(50) DEFAULT NULL,
  `validacion_fecha_llantas` varchar(50) DEFAULT NULL,
  `validacion_sello` varchar(50) DEFAULT NULL,
  `validacion_firma_almacen` varchar(50) DEFAULT NULL,
  `validacion_firma_proveedor` varchar(50) DEFAULT NULL,
  `vigilante_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vigilante_id` (`vigilante_id`),
  CONSTRAINT `fk_validacion_vigilante` FOREIGN KEY (`vigilante_id`) REFERENCES `auth_user` (`id`)
) 

CREATE TABLE `validacion_manual` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `numero_manual` varchar(100) NOT NULL,
  `ruta_imagen` varchar(255) NOT NULL,
  `validacion_sello` varchar(50) NOT NULL,
  `validacion_firma_almacen` varchar(50) NOT NULL,
  `validacion_firma_proveedor` varchar(50) NOT NULL,
  `vigilante_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vigilante_id` (`vigilante_id`),
  CONSTRAINT `fk_validacion_manual` FOREIGN KEY (`vigilante_id`) REFERENCES `auth_user` (`id`)
)


```

## Respaldo de la Información
Se recomienda realizar backups cada 15 días (o semanalmente si hay un alto volumen de registros) para garantizar la seguridad de la información.

## Instalación y Configuración
1. Clona el repositorio:
   ```bash
   git clone https://github.com/JhonatanUsugaSao6/Control-Activos
   ```
2. Instala las dependencias:
   ```bash
   SECRET_KEY = tu-clave-seguridad

    DEBUG = True o False

    ALLOWED_HOSTS = localhost, 127.0.0.1

    # Base de datos SQL Server (Siesa)
    ENGINE_SQL=tu-engine-siesa
    NAME_SQL=tu-tabla
    USER_SQL=tu-usuario
    PASSWORD_SQL=tu-contraseña
    HOST_SQL=tu-host
    PORT_SQL=tu-puerto
    DRIVER=tu-drive-odbc

    # Base de datos MySQL (Default)
    ENGINE_MYSQL=tu-engine
    NAME_MYSQL=tu-tabla
    USER_MYSQL=tu-usuario
    PASSWORD_MYSQL=tu-contraseña
    HOST_MYSQL=tu-host
    PORT_MYSQL=tu-puerto
    INIT=SET sql_mode='STRICT_TRANS_TABLES'
   ```

3. Crear archivo .env:
   ```bash
   pip install -r requirements.txt
   ```

4. Realiza las migraciones de la base de datos:
   ```bash
   python manage.py migrate
   ```
5. Inicia el servidor:
   ```bash
   python manage.py runserver
   ```



