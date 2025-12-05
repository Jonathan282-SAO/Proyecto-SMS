# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.models import Usuario, Grupo, db, Mensaje
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from threading import Thread
from app.forms import LoginForm, ChangePasswordForm, GroupForm

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if request.method == 'POST':
        # Primero intentar validación WTForms/CSRF
        if form.validate_on_submit():
            # Compatibilidad: tomar dato desde el formulario WTForms si existe, sino desde request.form
            username = None
            password = None
            if hasattr(form, 'username') and getattr(form, 'username') is not None:
                try:
                    username = form.username.data.strip() if form.username.data is not None else None
                except Exception:
                    username = None
            if hasattr(form, 'password') and getattr(form, 'password') is not None:
                try:
                    password = form.password.data
                except Exception:
                    password = None
            if not username:
                username = request.form.get('perfil') or request.form.get('username') or ''
            if not password:
                password = request.form.get('contrasenna') or request.form.get('password') or ''
        else:
            # Fallback: si la validación WTForms/CSRF falla (p. ej. token faltante), intentar con los campos tradicionales
            username = request.form.get('perfil') or request.form.get('username') or ''
            password = request.form.get('contrasenna') or request.form.get('password') or ''
            # Si no vienen credenciales, entonces informar y redirigir
            if not username or not password:
                flash('Datos de login inválidos', 'error')
                return redirect(url_for('main.login'))

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            # Si el modo mantenimiento está activo, solo permitir login a administradores.
            from app.models import Settings
            settings = Settings.query.first()
            maintenance_active = False
            maintenance_message = None
            try:
                maintenance_active = bool(getattr(settings, 'maintenance', False))
                maintenance_message = getattr(settings, 'maintenance_message', None)
            except Exception:
                maintenance_active = False

            if maintenance_active and usuario.role != 'admin':
                # No iniciar sesión para usuarios normales durante mantenimiento; mostrar página de mantenimiento
                return render_template('maintenance.html', message=maintenance_message)

            # Permitir login (admin o sitio no en mantenimiento)
            session['logged_in'] = True
            session['username'] = usuario.username
            session['role'] = usuario.role
            flash("Sesión iniciada correctamente.", "success")
            if usuario.role == "admin":
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('main.home'))
        else:
            flash("Credenciales incorrectas", "error")
            return redirect(url_for('main.login'))
    return render_template('portal.html', form=form)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    return index()


@main_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "success")
    return redirect(url_for('main.index'))


@main_bp.route('/home', methods=['GET'] )
def home():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    messages = Mensaje.query.all()
    # pasar settings para que la UI de usuarios refleje configuraciones
    from app.models import Settings
    settings = Settings.query.first()
    return render_template('home.html', usuario=session.get('username'), messages=messages, settings=settings)


@main_bp.route('/redactar', methods=['GET', 'POST'])
def redactar():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        # procesar mensaje
        try:
            grupo_id = int(request.form.get('grupo', 0))
        except ValueError:
            flash('Grupo inválido', 'error')
            return redirect(url_for('main.redactar'))

        modalidad = (request.form.get('modalidad') or '').strip()
        asunto = (request.form.get('asunto') or '').strip()
        contenido = (request.form.get('mensaje') or '').strip()

        # Validaciones simples
        if not asunto or not contenido:
            flash('Asunto y contenido son obligatorios', 'error')
            return redirect(url_for('main.redactar'))
        if len(asunto) > 150 or len(contenido) > 4000:
            flash('Contenido demasiado largo', 'error')
            return redirect(url_for('main.redactar'))

        # Obtener el grupo
        grupo = Grupo.query.get_or_404(grupo_id)

        # Obtener el usuario que envía el mensaje
        usuario_actual = Usuario.query.filter_by(username=session['username']).first()

        if not usuario_actual:
            flash("Usuario no encontrado", "error")
            return redirect(url_for('main.redactar'))

        # Guardar un registro del mensaje "enviado"
        nuevo_mensaje = Mensaje(
            asunto=asunto,
            contenido=contenido,
            modalidad=modalidad,
            grupo_id=grupo.id,
            usuario_id=usuario_actual.id
        )
        db.session.add(nuevo_mensaje)
        db.session.commit()

        # Envío en background para no bloquear la petición
        def send_background(mensaje_id, grupo_id):
            try:
                mensaje = Mensaje.query.get(mensaje_id)
                grupo_local = Grupo.query.get(grupo_id)
                if not mensaje or not grupo_local:
                    return
                for u in grupo_local.usuarios:
                    # Integración real con SMS/Email aquí
                    current_app.logger.info(f"📨 (bg) Enviando a {u.username} -> {u.email}")
            except Exception as e:
                current_app.logger.exception('Error en envío background: %s', e)

        Thread(target=send_background, args=(nuevo_mensaje.id, grupo.id), daemon=True).start()

        # Mantener al usuario en la pestaña de redactar y mostrar confirmación
        flash('Mensaje enviado correctamente', 'success')
        return redirect(url_for('main.redactar'))
    grupos = Grupo.query.all()
    return render_template('redactar.html', 
                           usuario=session['username'],
                           grupos=grupos, 
                           year=2025)


@main_bp.route('/notificaciones')
def notificaciones():
    # Mostrar tanto Mensaje (envíos) como Campaña en el listado de notificaciones
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    # parámetros de filtrado y paginación
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    limit = 10

    # Obtener mensajes y campañas
    mensajes = Mensaje.query.order_by(Mensaje.fecha_envio.desc()).all()
    from app.models import Campaña
    campañas = Campaña.query.order_by(Campaña.date.desc()).all()

    notifications = []
    # Añadir solo campañas activas (evitar mostrar campañas inactivas en notificaciones)
    for c in campañas:
        try:
            is_active = getattr(c, 'active', True)
        except Exception:
            is_active = True
        if not is_active:
            continue
        notifications.append({
            'type': 'campaign',
            'title': c.name or (c.message[:80] + '...'),
            'text': c.message,
            'sent_at': c.date,
            'author': 'Sistema',
            'priority': (getattr(c, 'priority', None) or 'baja')
        })
    for m in mensajes:
        notifications.append({
            'type': 'message',
            'title': m.asunto or ('Mensaje ' + str(m.id)),
            'text': m.contenido,
            'sent_at': m.fecha_envio,
            'author': (m.usuario.username if getattr(m, 'usuario', None) and m.usuario else 'Sistema'),
            'priority': 'baja'
        })

    # ordenar por fecha descendente
    notifications = sorted([n for n in notifications if n.get('sent_at')], key=lambda x: x['sent_at'], reverse=True)

    # Filtrar por rango de fechas si se proporcionan
    def in_date_range(n):
        if not from_date and not to_date:
            return True
        try:
            sent = n.get('sent_at')
            if not sent:
                return False
            if from_date:
                fd = datetime.strptime(from_date, '%Y-%m-%d')
                if sent < fd:
                    return False
            if to_date:
                td = datetime.strptime(to_date, '%Y-%m-%d')
                # include the whole day
                td_end = td.replace(hour=23, minute=59, second=59)
                if sent > td_end:
                    return False
            return True
        except Exception:
            return True

    filtered = [n for n in notifications if in_date_range(n)]
    total = len(filtered)

    # paginar por página
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    if page > total_pages:
        page = total_pages
    start = (page - 1) * limit
    end = start + limit
    page_slice = filtered[start:end]

    return render_template('notificaciones.html', usuario=session.get('username'), notifications=page_slice, total_notifications=total, page=page, total_pages=total_pages, limit=limit, from_date=from_date, to_date=to_date)


@main_bp.route('/extras/ayuda')
def ayuda():
    if not session.get('logged_in'):
        return redirect(url_for('main.index'))
    # Obtener soporte desde Settings si está disponible
    from app.models import Settings
    settings = Settings.query.first()
    support = settings.support_email if settings and settings.support_email else 'etecsa.ayuda@nauta.com.cu'
    return render_template('extras/ayuda.html', usuario=session.get('username') or session.get('usuario') or 'Usuario', year=2025, support_email=support, settings=settings)


@main_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        actual = request.form['actual']
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']
        usuario_actual = session['username']
        user = Usuario.query.filter_by(username=usuario_actual).first()
        if not user or not check_password_hash(user.password_hash, actual):
            flash('Contraseña actual incorrecta', 'error')
            return redirect(url_for('main.change_password'))
        if nueva != confirmar:
            flash('La nueva contraseña no coincide con la confirmación', 'error')
            return redirect(url_for('main.change_password'))
        user.password_hash = generate_password_hash(nueva)
        db.session.commit()
        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('main.home'))
    return render_template('change_password.html')


@main_bp.route('/grupos',  methods=['GET', 'POST'])
def grupos():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    usuarios = Usuario.query.all()
    grupos = Grupo.query.all()

    # Instanciar el formulario y asegurar que los choices estén definidos
    form = GroupForm()
    try:
        # si WTForms está disponible, asignar choices para el SelectMultipleField
        if hasattr(form, 'usuarios'):
            form.usuarios.choices = [(u.id, u.username or ("ID %d" % u.id)) for u in usuarios]
    except Exception:
        pass

    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Datos de grupo inválidos', 'error')
            return redirect(url_for('main.grupos'))

        # nombre puede venir desde WTForms o directamente desde request.form
        try:
            nombre = form.nombre.data.strip() if getattr(form, 'nombre', None) and form.nombre.data is not None else None
        except Exception:
            nombre = None
        if not nombre:
            nombre = (request.form.get('nombre') or '').strip()
        user_ids = request.form.getlist('usuarios')  # lista de IDs seleccionados

        # Crear grupo
        nuevo_grupo = Grupo(nombre=nombre)
        for uid in user_ids:
            try:
                uid_i = int(uid)
            except ValueError:
                continue
            usuario = Usuario.query.get(uid_i)
            if usuario:
                nuevo_grupo.usuarios.append(usuario)

        db.session.add(nuevo_grupo)
        try:
            db.session.commit()
            flash("Grupo creado correctamente", "success")
        except IntegrityError:
            db.session.rollback()
            flash('Ya existe un grupo con ese nombre', 'error')

        return redirect(url_for('main.grupos'))

    return render_template('grupos.html', 
                           usuario=session.get('username'), 
                           usuarios=usuarios, 
                           grupos=grupos,
                           form=form)


@main_bp.route('/grupos/<int:id>/editar', methods=['GET', 'POST'], endpoint='editar_grupo')
def editar_grupo(id):
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    grupo = Grupo.query.get_or_404(id)
    usuarios = Usuario.query.order_by(Usuario.username).all()

    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        if not nombre:
            flash('El nombre del grupo es obligatorio', 'error')
            return redirect(url_for('editar_grupo', id=id))

        # actualizar nombre
        grupo.nombre = nombre

        # actualizar usuarios asociados
        selected = request.form.getlist('usuarios') or []
        grupo.usuarios = []
        for uid in selected:
            try:
                u = Usuario.query.get(int(uid))
                if u:
                    grupo.usuarios.append(u)
            except Exception:
                continue

        try:
            db.session.commit()
            flash('Grupo actualizado correctamente', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Error al actualizar el grupo (nombre duplicado?)', 'error')

        return redirect(url_for('main.grupos'))

    return render_template('editar_grupo.html', grupo=grupo, usuarios=usuarios)


@main_bp.route('/grupos/<int:id>/eliminar', methods=['POST'], endpoint='eliminar_grupo')
def eliminar_grupo(id):
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    grupo = Grupo.query.get_or_404(id)

    try:
        # Eliminar mensajes asociados primero para evitar errores de FK
        from app.models import Mensaje
        db.session.query(Mensaje).filter(Mensaje.grupo_id == id).delete()
        # detach relations user<->group
        grupo.usuarios = []
        db.session.delete(grupo)
        db.session.commit()
        flash('Grupo eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('Error al eliminar grupo: %s', e)
        flash('Error al eliminar el grupo', 'error')

    return redirect(url_for('main.grupos'))


    
