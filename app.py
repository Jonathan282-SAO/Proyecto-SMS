from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from werkzeug.routing import BuildError

app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=True)
    role = db.Column(db.String(20), default='user')

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, pw)

# Nuevo modelo para ajustes del sistema
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(200), nullable=True)
    support_email = db.Column(db.String(200), nullable=True)
    default_page = db.Column(db.String(50), nullable=True)
    max_concurrent = db.Column(db.Integer, default=5)
    maintenance = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Campaña(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Grupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class Mensaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asunto = db.Column(db.String(150))
    contenido = db.Column(db.Text)
    modalidad = db.Column(db.String(50))
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)

    grupo = db.relationship('Grupo', backref=db.backref('mensajes', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('mensajes', lazy=True))

# Crear las tablas
with app.app_context():
    db.create_all()

# Crear admin por defecto (si no existe)
def crear_admin_por_defecto():
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Llamar explícitamente al crear el admin en el contexto de la app
with app.app_context():
    crear_admin_por_defecto()
    # asegurar que exista una fila de Settings
    s = Settings.query.first()
    if not s:
        s = Settings(system_name='Mensajería Masiva', support_email='soporte@ejemplo.com',
                     default_page='home', max_concurrent=5, maintenance=False, maintenance_message='')
        db.session.add(s)
        db.session.commit()

# Decorador para proteger rutas admin
def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'admin':
            flash("Acceso denegado: se requiere cuenta administrativa.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('perfil')
        password = request.form.get('contrasenna')

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            session['logged_in'] = True
            session['username'] = usuario.username
            session['role'] = usuario.role
            flash("Sesión iniciada correctamente.", "success")
            if usuario.role == "admin":
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('home'))
        else:
            flash("Credenciales incorrectas", "error")
            return redirect(url_for('login'))
            
    return render_template('index.html')

# Alias para mantener compatibilidad con redirects a 'login'
@app.route('/login', methods=['GET', 'POST'])
def login():
    return index()

@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "success")
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html', usuario=session.get('username'))

@app.route('/admin')
def admin():
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('login'))
    return render_template('admin/admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('logged_in') and session.get('role') == 'admin':
        return render_template('admin/admin_dashboard.html', admin_user=session.get('username'))
    flash("Debe iniciar sesión como administrador", "error")
    return redirect(url_for('login'))

@app.route('/admin/users')
def admin_users():
    if session.get('logged_in') and session.get('role') == 'admin':
        users = Usuario.query.all()
        return render_template('admin/admin_users.html', admin_user=session.get('username'), users=users)
    flash("Debe iniciar sesión como administrador", "error")
    return redirect(url_for('login'))

@app.route('/admin/users/add', methods=['POST'])
def add_user():
    if session.get('logged_in') and session.get('role') == 'admin':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        print(f"🔍 DEBUG - Datos recibidos: username={username}, email={email}, role={role}, password={'*' * len(password) if password else 'None'}")

        if not all([username, email, password, role]):
            flash("Todos los campos son obligatorios", "error")
            print("❌ ERROR - Campos faltantes")
            return redirect(url_for('admin_users'))

        # Verificar si el usuario o email ya existen
        existing_user = Usuario.query.filter(
            (Usuario.username == username) | (Usuario.email == email)
        ).first()
        
        if existing_user:
            flash("Nombre de usuario o email ya existe", "error")
            print(f"❌ ERROR - Usuario existente: {existing_user.username}")
            return redirect(url_for('admin_users'))

        try:
            nuevo_usuario = Usuario(username=username, email=email, role=role)
            nuevo_usuario.set_password(password)
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            ##print(f"✅ USUARIO CREADO - ID: {nuevo_usuario.id}, Username: {nuevo_usuario.username}")
            ##flash("Usuario agregado correctamente", "success")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR EN BD: {str(e)}")
            flash(f"Error al crear usuario: {str(e)}", "error")
            
        return redirect(url_for('admin_users'))

    flash("No autorizado", "error")
    return redirect(url_for('login'))

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('login'))

    user = Usuario.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        role = request.form.get('role')
        if role in ['admin', 'user']:
            user.role = role

        db.session.commit()
        flash("Usuario actualizado correctamente", "success")
        return redirect(url_for('admin_users'))

    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST', 'GET'])
def delete_user(user_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('login'))

    user = Usuario.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado correctamente", "success")

    return redirect(url_for('admin_users'))


@app.route('/admin/campaigns')
def admin_campaigns():
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Debe iniciar sesión como administrador", "error")
        return redirect(url_for('login'))
    campaigns = Campaña.query.order_by(Campaña.date.desc()).all()
    return render_template('admin/admin_campaigns.html', campaigns=campaigns)

@app.route('/admin/campaigns', methods=['POST'])
def crear_campaña():
    name = request.form.get('campaign_name')
    message = request.form.get('campaign_message')
    if name and message:
        nueva = Campaña(name=name, message=message)
        db.session.add(nueva)
        db.session.commit()
        flash("Campaña creada", "success")
    else:
        flash("Todos los campos son requeridos", "error")
    return redirect(url_for('admin_campaigns'))

@app.route('/admin/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST'], endpoint='admin_campaigns_edit')
def edit_campaign(campaign_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('login'))

    campaña = Campaña.query.get_or_404(campaign_id)

    if request.method == 'POST':
        campaña.name = request.form.get('campaign_name')
        campaña.message = request.form.get('campaign_message')
        db.session.commit()
        flash("Campaña actualizada correctamente", "success")
        return redirect(url_for('admin_campaigns'))

    return render_template('admin/edit_campaign.html', campaign=campaña)

@app.route('/admin/campaigns/<int:campaign_id>/delete', methods=['POST'], endpoint='admin_campaigns_delete')
def delete_campaign(campaign_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('login'))

    campaña = Campaña.query.get_or_404(campaign_id)
    db.session.delete(campaña)
    db.session.commit()
    flash("Campaña eliminada correctamente", "success")
    return redirect(url_for('admin_campaigns'))


@app.route('/redactar', methods=['GET', 'POST'])
def redactar():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        grupo_id = request.form['grupo']
        modalidad = request.form['modalidad']
        asunto = request.form['asunto']
        mensaje = request.form['mensaje']

        # Aquí procesas el mensaje como sea necesario (guardar en BD, enviar, etc.)

        return redirect(url_for('notificaciones'))  # o donde desees redirigir

    # Si es GET, obtenemos los grupos desde la base de datos
    grupos = Grupo.query.all()
    return render_template('redactar.html', usuario=session['username'], grupos=grupos, year=2025)


@app.route('/admin/reports')
def admin_reports():
    if session.get('logged_in') and session.get('role') == 'admin':
        return render_template('admin/admin_reports.html', admin_users=session.get('username'))
    flash("Debe iniciar sesión como administrador", "error")
    return redirect(url_for('login'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@require_admin
def admin_settings():
    settings = Settings.query.first()
    if request.method == 'POST':
        # Leer valores del formulario (nombres coincidentes con template)
        system_name = request.form.get('systemName') or request.form.get('system_name')
        support_email = request.form.get('supportEmail') or request.form.get('support_email')
        default_page = request.form.get('defaultPage') or request.form.get('default_page')
        try:
            max_concurrent = int(request.form.get('maxConcurrent') or request.form.get('max_concurrent') or 5)
            if max_concurrent < 1:
                max_concurrent = 1
        except ValueError:
            max_concurrent = 5
        maintenance = True if request.form.get('maintenance') in ('on', 'true', '1') else False
        maintenance_message = request.form.get('maintenanceMessage') or request.form.get('maintenance_message') or ''

        if not settings:
            settings = Settings()
            db.session.add(settings)

        settings.system_name = system_name
        settings.support_email = support_email
        settings.default_page = default_page
        settings.max_concurrent = max_concurrent
        settings.maintenance = maintenance
        settings.maintenance_message = maintenance_message
        settings.updated_at = datetime.utcnow()

        db.session.commit()
        flash("Ajustes guardados correctamente.", "success")
        return redirect(url_for('admin_settings'))

    # GET: renderizar plantilla. pasar objetos necesarios.
    return render_template('admin/admin_settings.html',
                            settings=settings,
                            admin_user=session.get('username'),
                            support_email=(settings.support_email if settings else 'soporte@ejemplo.com'),
                            year=datetime.utcnow().year)

@app.route('/notificaciones')
def notificaciones():
    return render_template('notificaciones.html', usuario=session.get('username'))

@app.route('/extras/ayuda')
def ayuda():
    # si quieres proteger la ruta:
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template(
        'extras/ayuda.html',
        usuario=session.get('username') or session.get('usuario') or 'Usuario',
        year=datetime.utcnow().year,
        support_email='soporte@ejemplo.com'
    )

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        actual = request.form['actual']
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        usuario_actual = session['username']
        user = Usuario.query.filter_by(username=usuario_actual).first()

        if not user or not check_password_hash(user.password_hash, actual):
            flash('Contraseña actual incorrecta', 'error')
            return redirect(url_for('change_password'))

        if nueva != confirmar:
            flash('La nueva contraseña no coincide con la confirmación', 'error')
            return redirect(url_for('change_password'))

        user.password_hash = generate_password_hash(nueva)
        db.session.commit()

        print(f"Nueva contraseña hasheada guardada: {user.password_hash}")

        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('home'))

    return render_template('change_password.html')

@app.route('/grupos')
def grupos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('grupos.html', usuario=session.get('username'))

@app.route('/admin/campaigns/add', methods=['GET', 'POST'], endpoint='admin_campaigns_add')
def admin_campaigns_add():
    """
    Alias seguro usado por plantillas que llaman a url_for('admin_campaigns_add').
    Si es POST delega en crear_campaña(), si es GET redirige al listado.
    """
    if request.method == 'POST':
        return crear_campaña()
    return redirect(url_for('admin_campaigns'))

# Registrar alias (endpoints usados por plantillas) para evitar BuildError
app.add_url_rule('/admin/campaigns/<int:campaign_id>/edit',
                 endpoint='edit_campaign',
                 view_func=edit_campaign,
                 methods=['GET', 'POST'])

app.add_url_rule('/admin/campaigns/<int:campaign_id>/delete',
                 endpoint='delete_campaign',
                 view_func=delete_campaign,
                 methods=['POST'])

@app.context_processor
def utility_processor():
    def safe_url_for(endpoint, _fallback=None, **values):
        """
        Intenta url_for(endpoint). Si falla devuelve url_for(_fallback) o '#' si no existe.
        Uso en templates: {{ safe_url_for('admin_campaigns_add', _fallback='admin_campaigns') }}
        """
        try:
            return url_for(endpoint, **values)
        except BuildError:
            if _fallback:
                try:
                    return url_for(_fallback, **values)
                except BuildError:
                    return '#'
            return '#'
    return dict(safe_url_for=safe_url_for)

if __name__ == '__main__':
    app.run(debug=True)
