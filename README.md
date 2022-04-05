# ERP
_Herramientas de control empresarial_

## Descripción

En el repositorio se encuentran los módulos necesarios para el control
de actividades empresariales de una pequeña o mediana organización.
Se hace uso de bootstrap para dar formato general a toda la aplicación 
y se utiliza JQuery para realizar algunas acciones dinámicas dentro 
de al estructura de la aplicación.

## Instalación

Es necesario contar como minimo con los paquetes indicados en el archivo
"Docs/dependencies.txt" para el correcto funcionamiento de cada sección.

Se debe iniciar un proyecto sobre le cual se colocarán los modulos

    django-admin startproyect <nombre>

Los módulos se instalan con el comando

    python -m pip install --user <paquete>

Se realiza la configuracion dentro del proyecto

    Settings.py
        
        - SECRET_KEY
        - INSTALLED_APPS
        - TEMPLATES['DIRS']=[os.path.join(BASE_DIR,'templates/')]
        - DATABASES

        Se agrega al final del archivo, para utilizar elementos base
        - CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
        - CRISPY_TEMPLATE_PACK = "bootstrap5"
        - AUTH_USER_MODEL = 'usuarios.Usuario'
        - LOGIN_REDIRECT_URL = reverse_lazy('index')
        - LOGOUT_REDIRECT_URL = reverse_lazy('index')

    urls.py

        Se agregan las urls asociadas a cada uno de los módulos instalados

Se ejecutan las migraciones y creacion de usuario administrador

    python -manage.py makemigrations
    python -manage.py migrate
    python -manage.py createsuperuser

### Desarrollo

    python -manage.py runserver

### Producción

Es necesario desactivar el debug en settings (adicional a la configuracion anterior)

    DEBUG = False
    ALLOWED_HOSTS = ['localhost', 'ip-servidor', 'nombre-servidor']

#### NGinx 

Se descomprime Nginx (version descargada de nginx.org) y se coloca la carpeta en el disco `C:\`

Se crean las carpetas sites-available, sites-enable

    C:\nginx-1.21.6\sites-enable
    C:\nginx-1.21.6\sites-available
    
Se descomprimen los archivos nginx_waitress.rar [(material de apoyo del autor)](https://github.com/Johnnyboycurtis/webproject)

Se copia el archivo `runserver.py` a la misma ubicacion de "manage.py" y se debe modificar "webproject.wsgi" por "<projecto>.wsgi"

Se mofica el archivo "webproject_nginx.conf" validando principalmente:
* server_name (nombre del equipo)
* alias de location media (si es necesario, path completo)
* alias de static (si es necesario, path completo)
* proxy_pass (redirige a la configuración del waitress en el archivo runserver.py)

*Todo esto necesité agregarlo para que funcionaran los formularios con la validación de token*

    # para evitar el CrossSite Scripting
    proxy_set_header        X-Real_IP       $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-NginX-Proxy   true;
    proxy_set_header        Host            $http_host;
    proxy_set_header        Upgrade         $http_upgrade;
    proxy_pass_header       Set-Cookie;
    proxy_pass              http://localhost:8080;


Se copia el archivo modificado "webproject_nginx.conf" a las carpetas site enable y available de nginx.

*Se moficia el archivo "nginx.conf". Se hace un include dentro de http, despues de "application/octet-stream;"*

    http {
        include       mime.types;
        default_type  application/octet-stream;

        include         C:\\nginx-1.21.6\\sites-enable\\webproject_nginx.conf;
        ...

        server {
            listen       10; #se cambia este puerto para dejar libre el 80 para nuestro servidor
            ...
        }
    }

Se valida la configuracion de nginx con la terminal ejecutando `nginx.exe -t`. Debiera mostrarse unos mensajes como estos:

    nginx: the configuration file C:\nginx-1.21.6/conf/nginx.conf syntax is ok
    nginx: configuration file C:\nginx-1.21.6/conf/nginx.conf test is successful


> Si hay unproblema con el puerto 80 que esta siendo utilizado se puede cambar el puerto de nuestro servidor en los archivos "webproject_nginx.conf" de sites enable y available que copiamos.

**Para ejecutar**

* Se ejecuta nginx.exe (se cierra el proceso desde el administrador de tareas, no hay otra forma)
* Se ejecuta runserver.py (desde el ambiente virtual, para iniciar waitress)

