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

    pip install -r Docs/dependencies.txt

Se debe iniciar un proyecto sobre le cual se colocarán los modulos

    django-admin startproject <nombre>

Los módulos se instalan con el comando

    python -m pip install --user <paquete>

Se realiza la configuracion dentro del proyecto

    Settings.py
        
        - SECRET_KEY
        - INSTALLED_APPS
            'django.contrib.humanize',
            'crispy_forms',
            'crispy_bootstrap5',
            'simple_history',
            'usuarios',
            '<paquetes-instalados>'
        - TEMPLATES['DIRS']=[os.path.join(BASE_DIR,'templates/')] # import os
        - DATABASES
        - LANGUAGE_CODE = 'es-GT'
        - TIME_ZONE = 'America/Guatemala'
        - USE_I18N = True
        - USE_TZ = False # para usar hora local del equipo

    Se agrega la siguiente configuración al final del archivo:
        # Trusted Origins for NGinx proxy
        - CSRF_TRUSTED_ORIGINS = ["https://<url_configurada_en_el_servidor>"]
        # Plantillas bootstrap
        - CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
        - CRISPY_TEMPLATE_PACK = "bootstrap5"
        # Reemplazar el usario en settings del proyecto
        - AUTH_USER_MODEL = 'usuarios.Usuario'
        - LOGIN_REDIRECT_URL = reverse_lazy('index')        # from django.urls import reverse_lazy
        - LOGOUT_REDIRECT_URL = reverse_lazy('index')       # from django.urls import reverse_lazy
        - STATIC_ROOT = os.path.join(BASE_DIR, 'static')
        # Configuración de correo (pruebas y producción)
        -if DEBUG:
            EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
            EMAIL_FILE_PATH = '<ruta para generar los archivos>' # ruta para genrear archivos
        else:
            EMAIL_USE_TLS = True
            EMAIL_USE_SSL = False
            EMAIL_HOST = ''
            EMAIL_HOST_USER = ''
            EMAIL_HOST_PASSWORD = ''
            EMAIL_PORT = 
    urls.py
        - Se agregan las urls asociadas a cada uno de los módulos instalados
        En el caso de *usuarios* se agrega _path('', include('usuarios.urls')),_

Se ejecutan las migraciones y creacion de usuario administrador

    python manage.py makemigrations <app>
    python manage.py migrate
    python manage.py collectstatic
    python manage.py createsuperuser

Eliminar las migraciones de una app
    
    python manage.py migrate <--fake> <app> zero 

Se cargan librerías adicionales a la ruta usuarios/static:
    
- jquery (js)           # Download the compressed, production jQuery 3.6.0 y map (jquery.min.js)
- bootstrap (js y css)  # Compiled CSS and JS

### Desarrollo

    python -manage.py runserver

### Producción

Es necesario desactivar el debug en settings (adicional a la configuracion anterior)

    DEBUG = False
    ALLOWED_HOSTS = ['localhost', 'ip-servidor', 'nombre-servidor']

#### Certificados
[(Instalar OpenSSL En Windows)](https://tecadmin.net/install-openssl-on-windows/)
[(Generar certificados)](https://stackoverflow.com/questions/55407860/generate-cert-pem-and-key-pem-on-windows)

    Se deben crear los certificados correspondientes cert.pem y key.pem

    En la consola, con permisos de administrador, se ejecutan:
        _Agrega variables de entorno a las sesión_
        > set OPENSSL_CONF=C:\Program Files\OpenSSL-Win64\bin\openssl.cfg 
        > set Path=%Path%;C:\Program Files\OpenSSL-Win64\bin
        _Genera los certificados (5 años aproximadamente, se puede modificar)_
        > openssl req -x509 -newkey rsa:4096 -nodes -out <ruta>\cert.pem -keyout <ruta>\key.pem -days 1830

    El proceso solicita informacion adicional para generar el certificado

#### NGinx 

Se descomprime Nginx (version descargada de nginx.org) y se coloca la carpeta en el disco `C:\`

Se crean las carpetas sites-available, sites-enable

    C:\nginx-1.21.6\sites-enable
    C:\nginx-1.21.6\sites-available
    
Se descomprimen los archivos nginx_waitress.rar [(material de apoyo del autor)](https://github.com/Johnnyboycurtis/webproject) O los archivos modificados agregados en el proyecto "Docs\Servidor Produccion"

    - cert.pem
    - key.pem
    - conf\nginx.conf
    - sites-available\cartera_nginx.conf
    - sites-enable\cartera_nginx.conf
    - servidor\runserver.py

Se copia el archivo `runserver.py` a la misma ubicacion de "manage.py" y se debe modificar "webproject.wsgi" por "<projecto>.wsgi"

Se mofica el archivo "webproject_nginx.conf" validando principalmente:
* server_name (nombre del equipo)
* alias de location media (si es necesario, path completo)
* alias de static (si es necesario, path completo)
* proxy_pass (redirige a la configuración del waitress en el archivo runserver.py)

*En location _los comentados pueden ser opcionales_*

    # para evitar el CrossSite Scripting
    #proxy_set_header        X-Real_IP       $remote_addr;
    #proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    #proxy_set_header        X-NginX-Proxy   true;
    #proxy_set_header        Host            $http_host;
    #proxy_set_header        Upgrade         $http_upgrade;
    proxy_pass_header       Set-Cookie;
    proxy_pass              http://localhost:8080;


Se copia el archivo modificado "<webproject_nginx>.conf" a las carpetas site enable y available de nginx.

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

