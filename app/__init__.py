# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, url_for, flash, session
from werkzeug.routing import BuildError

import os
try:
    from flask_wtf import CSRFProtect  # type: ignore[import-untyped]
except Exception:
    CSRFProtect = None

# Optional extensions will be initialized if available (graceful fallback)
try:
    from flask_migrate import Migrate  # type: ignore[import-untyped]
except Exception:
    Migrate = None


def create_app():
    # Asegurar que Flask pueda encontrar las plantillas y assets dentro del paquete `app/`
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app_pkg_dir = os.path.join(base_dir, 'app')
    templates_dir = os.path.join(app_pkg_dir, 'templates')
    static_dir = os.path.join(app_pkg_dir, 'static')

    app = Flask(__name__, instance_relative_config=True, template_folder=templates_dir, static_folder=static_dir)
    # Cargar configuración desde `instance/config.py` si existe.
    app.config.from_pyfile('config.py', silent=True)

    # Valores por defecto (se pueden sobrescribir desde `instance/config.py`)
    # Seguridad: obtener SECRET_KEY desde variable de entorno si está disponible
    # Use a non-empty secret: prefer env var, then existing config value, otherwise fall back.
    env_secret = os.environ.get('SECRET_KEY')
    existing = app.config.get('SECRET_KEY')
    if env_secret:
        app.config['SECRET_KEY'] = env_secret
    elif existing:
        app.config['SECRET_KEY'] = existing
    else:
        app.config['SECRET_KEY'] = 'clave_secreta'
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.environ.get('DATABASE_URL', 'sqlite:///app.db'))
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    # Limitar tamaño máximo de carga (2 MB por defecto)
    app.config.setdefault('MAX_CONTENT_LENGTH', 2 * 1024 * 1024)
    # CSRF config (Flask-WTF)
    app.config.setdefault('WTF_CSRF_ENABLED', True)
    # Ensure there is a CSRF secret available (Flask-WTF may require it). Prefer explicit config, else use SECRET_KEY.
    if not app.config.get('WTF_CSRF_SECRET_KEY'):
        app.config['WTF_CSRF_SECRET_KEY'] = app.config.get('SECRET_KEY')

    # Asegurar que `app.secret_key` tiene un valor usable para la sesión.
    app.secret_key = app.config.get('SECRET_KEY')

    # Seguridad de cookies
    app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    # En producción activar SESSION_COOKIE_SECURE=True cuando haya HTTPS
    app.config.setdefault('SESSION_COOKIE_SECURE', os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True')

    # Usar modelos desde app.models
    from app.models import db, Usuario, Settings
    db.init_app(app)
    # Inicializar CSRF protection si está disponible
    try:
        csrf = CSRFProtect()
        csrf.init_app(app)
    except Exception:
        # si Flask-WTF no está instalado, continuamos pero sin CSRF
        csrf = None

    # Crear las tablas y datos iniciales
    with app.app_context():
        db.create_all()

        # Crear admin por defecto (si no existe) - sólo si NO hay variable de entorno ADMIN_PASSWORD
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(username='admin', email='admin@example.com', role='admin')
            admin_pw = os.environ.get('ADMIN_PASSWORD')
            if admin_pw:
                admin.set_password(admin_pw)
            else:
                # Si no se provee contraseña por entorno, generar una contraseña segura temporal
                admin.set_password('change-me-please')
            db.session.add(admin)
            db.session.commit()

        # Asegurar que exista una fila de Settings
        s = Settings.query.first()
        if not s:
            s = Settings(system_name='Mensajería Masiva', support_email='etecsa.ayuda@nauta.com.cu',
                         default_page='home', max_concurrent=5, maintenance=False, maintenance_message='')
            db.session.add(s)
            db.session.commit()

    # Registrar blueprints
    from app.routes import main_bp
    from app.admin_routes import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Si CSRF está disponible, eximir el blueprint de admin para evitar errores de token
    try:
        csrf_ext = app.extensions.get('csrf')
        if csrf_ext:
            try:
                csrf_ext.exempt(admin_bp)
            except Exception:
                pass
    except Exception:
        pass

    # Manejador amigable para errores CSRF (si flask_wtf está instalado)
    try:
        from flask_wtf.csrf import CSRFError  # type: ignore[import-untyped]
        @app.errorhandler(CSRFError)
        def handle_csrf(error):
            flash('Error de seguridad (CSRF): la sesión ha expirado o el formulario no es válido. Vuelve a intentarlo.', 'error')
            # Intentar redirigir al referer o a la página de ajustes
            ref = request.referrer
            try:
                return redirect(ref or url_for('admin.admin_settings'))
            except Exception:
                return redirect(url_for('main.index'))
    except Exception:
        pass

    # Middleware: redirigir a página de mantenimiento si está activo y el usuario no es admin
    @app.before_request
    def check_maintenance():
        # permitir acceso a recursos estáticos, al propio endpoint de mantenimiento y a rutas admin para administradores
        try:
            # Evitar usar la base de datos repetidamente si no es necesario
            from app.models import Settings
            s = Settings.query.first()
            if s and s.maintenance:
                # permisos: permitir si es admin
                if session.get('logged_in') and session.get('role') == 'admin':
                    return None
                # permitir acceso a la ruta de mantenimiento para mostrar el mensaje
                if request.endpoint in ('main.maintenance', 'static'):
                    return None
                # permitir acceso a login/logout para administradores que quieran autenticarse
                if request.endpoint in ('main.login', 'main.index', 'main.logout'):
                    return None
                # en cualquier otro caso redirigir a la página de mantenimiento
                return redirect(url_for('main.maintenance'))
        except Exception:
            # en caso de error no bloquear
            return None

    @app.context_processor
    def utility_processor():
        def safe_url_for(endpoint, _fallback=None, **values):
            try:
                return url_for(endpoint, **values)
            except BuildError:
                if _fallback:
                    try:
                        return url_for(_fallback, **values)
                    except BuildError:
                        return '#'
                return '#'

        # Añadir variables globales desde Settings para que las plantillas reflejen cambios inmediatamente
        from app.models import Settings
        def global_settings():
            s = Settings.query.first()
            return {
                'system_name': (s.system_name if s and s.system_name else 'Mensajería Masiva'),
                'support_email': (s.support_email if s and s.support_email else 'etecsa.ayuda@nauta.com.cu'),
                'maintenance': (s.maintenance if s else False),
                'maintenance_message': (s.maintenance_message if s and s.maintenance_message else '')
            }

        gs = global_settings()
        return dict(safe_url_for=safe_url_for, system_name=gs['system_name'], support_email=gs['support_email'], maintenance=gs['maintenance'], maintenance_message=gs['maintenance_message'])

    return app
