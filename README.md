# Proyecto Mensajería (Flask)

Resumen
--------
Aplicación web en Flask para gestión de usuarios, grupos y envío de notificaciones/campañas.

Estructura clave
- `app/` : paquete principal con rutas, modelos, formularios y plantillas.
- `instance/app.db` : base de datos SQLite usada en tiempo de ejecución.
- `app/static/` y `app/templates/` : assets y vistas.

Requisitos y puesta en marcha (Windows / PowerShell)
--------------------------------------------------
1) Crear y activar entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2) Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3) Configuración opcional (sobrescribir valores por defecto)

- Crea `instance/config.py` para valores locales (opcional):

```py
SECRET_KEY = 'cambia_esta_clave_segura'
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'
# Otros: WTF_CSRF_SECRET_KEY, SESSION_COOKIE_SECURE, etc.
```

4) Ejecutar la aplicación (desde la raíz del repo):

```powershell
# usando la factory
python run.py
# o con flask CLI
set FLASK_APP=run.py; set FLASK_ENV=development; flask run
```

Comportamiento importante: Modo mantenimiento
--------------------------------------------
- Cuando el administrador activa el `modo mantenimiento` desde el panel de administración (`/admin/settings`), los usuarios con rol `user` no podrán iniciar sesión: al intentarlo se mostrará la plantilla `maintenance.html` con el mensaje configurado.
- Solo los usuarios con `role == 'admin'` pueden iniciar sesión mientras dure el mantenimiento.
- La plantilla `maintenance.html` fue diseñada para no mostrar el footer global y contiene un botón para "Contactar soporte" y otro para "Volver al portal".

Notas sobre campañas y notificaciones
------------------------------------
- Las campañas ahora incluyen un campo `active` (boolean). Las campañas nuevas se crean inactivas por defecto; el administrador debe activarlas para que aparezcan en la lista de notificaciones y se envíen.
- Si tu base de datos no tiene la columna `active`, revisa el script `scripts/add_active_column.py` para agregarla o usa una migración con `Flask-Migrate`.

Pruebas y scripts útiles
------------------------
- `scripts/test_settings.py`: script sencillo que usa `Flask.test_client` para validar endpoints de settings y el middleware de mantenimiento. Para ejecutarlo en desarrollo:

```powershell
set FLASK_APP=run.py; set FLASK_ENV=development; python .\scripts\test_settings.py
```

Notas de seguridad y CSRF
------------------------
- La aplicación intenta usar `Flask-WTF`/`CSRFProtect` cuando está instalado. Algunas operaciones administrativas pueden requerir que el token CSRF esté presente en los formularios; en entornos de desarrollo o en scripts de prueba puede ser necesario deshabilitar temporalmente CSRF (`app.config['WTF_CSRF_ENABLED'] = False`) para automatizar peticiones.
- En producción no deshabilites CSRF: en su lugar, asegúrate de que los formularios incluyan `{{ form.csrf_token }}` o `{{ csrf_token() }}`.

Recomendaciones operativas
--------------------------
- Añadir `Flask-Migrate` para manejar cambios de esquema (recomendado).
- Realizar backups de `instance/app.db` antes de ejecutar scripts de alteración de esquema.
- Habilitar `SESSION_COOKIE_SECURE` en producción y usar HTTPS.

Contribuir
----------
Si contribuyes, abre un `pull request` con una descripción clara de cambios y añade tests cuando sea posible. Muchas gracias.
