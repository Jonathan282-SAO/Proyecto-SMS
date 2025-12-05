# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Usuario, Settings, Campaña, Grupo, Mensaje, db
from functools import wraps
from datetime import datetime, timedelta
import json
from sqlalchemy.exc import IntegrityError
from app.forms import AddUserForm, CampaignForm

admin_bp = Blueprint('admin', __name__)

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'admin':
            flash("Acceso denegado: se requiere cuenta administrativa.", "error")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin')
def admin():
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    return render_template('admin/admin.html')


@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('logged_in') and session.get('role') == 'admin':
        # Estadísticas básicas
        usuarios_count = Usuario.query.count()
        mensajes_count = Mensaje.query.count()
        grupos_count = Grupo.query.count()

        # Construir actividad reciente combinando mensajes y campañas
        mensajes = Mensaje.query.order_by(Mensaje.fecha_envio.desc()).limit(8).all()
        campañas = Campaña.query.order_by(Campaña.date.desc()).limit(8).all()

        latest_activity = []
        for m in mensajes:
            latest_activity.append({
                'title': m.asunto or 'Mensaje',
                'created_at': m.fecha_envio
            })
        for c in campañas:
            latest_activity.append({
                'title': c.name or 'Campaña',
                'created_at': c.date
            })

        # ordenar por fecha descendente y limitar
        latest_activity = sorted(latest_activity, key=lambda x: x.get('created_at') or datetime.utcnow(), reverse=True)[:8]

        # Series de actividad últimos 7 días (mensajes y campañas)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        labels = []
        messages_series = []
        campaigns_series = []
        for i in range(6, -1, -1):
            day_start = today - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            labels.append(day_start.strftime('%Y-%m-%d'))
            mcount = Mensaje.query.filter(Mensaje.fecha_envio >= day_start, Mensaje.fecha_envio < day_end).count()
            ccount = Campaña.query.filter(Campaña.date >= day_start, Campaña.date < day_end).count()
            messages_series.append(mcount)
            campaigns_series.append(ccount)

        return render_template('admin/admin_dashboard.html', admin_user=session.get('username'), usuarios_count=usuarios_count, mensajes_count=mensajes_count, grupos_count=grupos_count, latest_activity=latest_activity, activity_labels=labels, activity_messages=messages_series, activity_campaigns=campaigns_series)
    flash("Debe iniciar sesión como administrador", "error")
    return redirect(url_for('main.login'))


@admin_bp.route('/admin/users')
def admin_users():
    if session.get('logged_in') and session.get('role') == 'admin':
        users = Usuario.query.all()
        return render_template('admin/admin_users.html', admin_user=session.get('username'), users=users)
    flash("Debe iniciar sesión como administrador", "error")
    return redirect(url_for('main.login'))


@admin_bp.route('/admin/users/add', methods=['POST'])
def add_user():
    if session.get('logged_in') and session.get('role') == 'admin':
        form = AddUserForm()
        if not form.validate_on_submit():
            flash('Datos de usuario inválidos', 'error')
            return redirect(url_for('admin.admin_users'))

        # Compatibilidad con formulario WTForms o con request.form
        username = None
        email = None
        password = None
        role = None
        if hasattr(form, 'username') and getattr(form, 'username') is not None:
            try:
                username = form.username.data.strip()
            except Exception:
                username = None
        if hasattr(form, 'email') and getattr(form, 'email') is not None:
            try:
                email = form.email.data.strip()
            except Exception:
                email = None
        if hasattr(form, 'password') and getattr(form, 'password') is not None:
            try:
                password = form.password.data
            except Exception:
                password = None
        if hasattr(form, 'role') and getattr(form, 'role') is not None:
            try:
                role = form.role.data
            except Exception:
                role = None

        if not username:
            username = request.form.get('username')
        if not email:
            email = request.form.get('email')
        if not password:
            password = request.form.get('password')
        if not role:
            role = request.form.get('role')

        existing_user = Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first()
        if existing_user:
            flash("Nombre de usuario o email ya existe", "error")
            return redirect(url_for('admin.admin_users'))
        try:
            nuevo_usuario = Usuario(username=username, email=email, role=role)
            nuevo_usuario.set_password(password)
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario creado correctamente', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Nombre de usuario o email ya existe', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear usuario: {str(e)}", "error")
        return redirect(url_for('admin.admin_users'))
    flash("No autorizado", "error")
    return redirect(url_for('main.login'))


@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    user = Usuario.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        role = request.form.get('role')
        if role in ['admin', 'user']:
            user.role = role
        db.session.commit()
        flash("Usuario actualizado correctamente", "success")
        return redirect(url_for('admin.admin_users'))
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST', 'GET'])
def delete_user(user_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    user = Usuario.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado correctamente", "success")
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/admin/campaigns')
def admin_campaigns():
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Debe iniciar sesión como administrador", "error")
        return redirect(url_for('main.login'))
    campaigns = Campaña.query.order_by(Campaña.date.desc()).all()
    groups = Grupo.query.order_by(Grupo.nombre).all()

    # Mapear campaign.id -> lista de nombres de grupos objetivo
    campaign_targets = {}
    for c in campaigns:
        tg = []
        if getattr(c, 'target_groups', None):
            try:
                gids = json.loads(c.target_groups)
                if isinstance(gids, (list, tuple)):
                    for gid in gids:
                        try:
                            g = Grupo.query.get(int(gid))
                            if g:
                                tg.append(g.nombre)
                        except Exception:
                            continue
            except Exception:
                tg = []
        campaign_targets[c.id] = tg

    # Conteos: activos y programados
    now = datetime.utcnow()
    active_count = 0
    scheduled_count = 0
    for c in campaigns:
        try:
            if getattr(c, 'active', True):
                active_count += 1
        except Exception:
            active_count += 1
        try:
            if getattr(c, 'date', None) and c.date > now:
                scheduled_count += 1
        except Exception:
            pass

    return render_template('admin/admin_campaigns.html', campaigns=campaigns, groups=groups, campaign_targets=campaign_targets, active_count=active_count, scheduled_count=scheduled_count)


@admin_bp.route('/admin/campaigns', methods=['POST'], endpoint='admin_campaigns_add')
def admin_campaigns_add():
    # Requerir privilegios de administrador
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Debe iniciar sesión como administrador", "error")
        return redirect(url_for('main.login'))

    name = (request.form.get('campaign_name') or '').strip()
    message = (request.form.get('campaign_message') or '').strip()
    priority = (request.form.get('priority') or 'baja').strip().lower()
    if priority not in ('alta', 'media', 'baja'):
        priority = 'baja'
    # grupos seleccionados (multiple select)
    selected_groups = request.form.getlist('groups') or []
    # normalizar a ints válidos
    valid_group_ids = []
    for g in selected_groups:
        try:
            gid = int(g)
            # validar existencia
            if Grupo.query.get(gid):
                valid_group_ids.append(gid)
        except Exception:
            continue

    # Validación básica
    if not name or not message:
        flash("Todos los campos son requeridos", "error")
        return redirect(url_for('admin.admin_campaigns'))

    if len(name) > 200:
        flash("El nombre de la campaña es demasiado largo (máx. 200 caracteres).", "error")
        return redirect(url_for('admin.admin_campaigns'))

    try:
        # Por defecto crear campañas INACTIVAS; permitir activarlas en el formulario con 'active_now'
        active_flag = True if (request.form.get('active_now') in ('on', '1', 'true')) else False
        nueva = Campaña(name=name, message=message, target_groups=json.dumps(valid_group_ids) if valid_group_ids else None, priority=priority, active=active_flag)
        db.session.add(nueva)
        db.session.commit()
        flash("Campaña creada", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear campaña: {str(e)}", "error")

    return redirect(url_for('admin.admin_campaigns'))


@admin_bp.route('/admin/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST'], endpoint='admin_campaigns_edit')
def edit_campaign(campaign_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    campaña = Campaña.query.get_or_404(campaign_id)
    if request.method == 'POST':
        campaña.name = request.form.get('campaign_name')
        campaña.message = request.form.get('campaign_message')
        db.session.commit()
        flash("Campaña actualizada correctamente", "success")
        return redirect(url_for('admin.admin_campaigns'))
    return render_template('admin/edit_campaign.html', campaign=campaña)


@admin_bp.route('/admin/campaigns/<int:campaign_id>/delete', methods=['POST'], endpoint='admin_campaigns_delete')
def delete_campaign(campaign_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    campaña = Campaña.query.get_or_404(campaign_id)
    db.session.delete(campaña)
    db.session.commit()
    flash("Campaña eliminada correctamente", "success")
    return redirect(url_for('admin.admin_campaigns'))


@admin_bp.route('/admin/campaigns/delete', methods=['POST'], endpoint='admin_campaigns_delete_simple')
def delete_campaign_simple():
    # Variante que recibe campaign_id desde el formulario (útil para modales que sólo envían el id)
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    campaign_id = request.form.get('campaign_id')
    if not campaign_id:
        flash('ID de campaña requerido', 'error')
        return redirect(url_for('admin.admin_campaigns'))
    try:
        campaign_id = int(campaign_id)
    except ValueError:
        flash('ID de campaña inválido', 'error')
        return redirect(url_for('admin.admin_campaigns'))
    campaña = Campaña.query.get_or_404(campaign_id)
    try:
        db.session.delete(campaña)
        db.session.commit()
        flash('Campaña eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la campaña: {e}', 'error')
    return redirect(url_for('admin.admin_campaigns'))


@admin_bp.route('/admin/campaigns/<int:campaign_id>/toggle', methods=['POST'], endpoint='admin_campaigns_toggle')
def toggle_campaign(campaign_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    campaña = Campaña.query.get_or_404(campaign_id)
    # Alternar la bandera active (si no existe la columna en BD, esto puede fallar hasta ejecutar el script de migración)
    try:
        campaña.active = not (getattr(campaña, 'active', True))
        db.session.commit()
        flash("Campaña activada" if campaña.active else "Campaña desactivada", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al cambiar el estado de la campaña: {e}", "error")
    return redirect(url_for('admin.admin_campaigns'))


@admin_bp.route('/admin/campaigns/<int:campaign_id>/schedule', methods=['POST'], endpoint='admin_campaigns_schedule')
def schedule_campaign(campaign_id):
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    campaña = Campaña.query.get_or_404(campaign_id)
    sched = request.form.get('scheduled_at') or request.form.get('schedule_date')
    if not sched:
        flash('Fecha de programación requerida', 'error')
        return redirect(url_for('admin.admin_campaigns'))
    # Esperamos entrada tipo 'YYYY-MM-DDTHH:MM' (datetime-local). Convertir a datetime.
    try:
        # Normalizar posibles formatos (entrada sin zona: datetime-local HTML5)
        if 'T' in sched:
            # datetime-local HTML5
            dt = datetime.strptime(sched, '%Y-%m-%dT%H:%M')
        else:
            # intentar con espacio
            dt = datetime.strptime(sched, '%Y-%m-%d %H:%M')

        # Si el cliente envía el offset de zona (en minutos), ajustarlo para almacenar UTC
        tz_offset = request.form.get('tz_offset')
        if tz_offset is not None and tz_offset != '':
            try:
                offset_min = int(tz_offset)
                # getTimezoneOffset returns minutes to add to local time to get UTC
                dt = dt + timedelta(minutes=offset_min)
            except Exception:
                pass

        campaña.date = dt
        db.session.commit()
        flash('Campaña programada correctamente', 'success')
    except ValueError:
        flash('Formato de fecha inválido. Usa YYYY-MM-DDTHH:MM', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al programar la campaña: {e}', 'error')
    return redirect(url_for('admin.admin_campaigns'))


@admin_bp.route('/admin/campaigns/schedule', methods=['POST'], endpoint='admin_campaigns_schedule_simple')
def schedule_campaign_simple():
    # Variante que recibe campaign_id desde el formulario (más simple para submit desde modal)
    if not (session.get('logged_in') and session.get('role') == 'admin'):
        flash("Acceso denegado", "error")
        return redirect(url_for('main.login'))
    campaign_id = request.form.get('campaign_id')
    if not campaign_id:
        flash('ID de campaña requerido', 'error')
        return redirect(url_for('admin.admin_campaigns'))
    try:
        campaign_id = int(campaign_id)
    except ValueError:
        flash('ID de campaña inválido', 'error')
        return redirect(url_for('admin.admin_campaigns'))
    # Reusar la lógica de programación
    campaña = Campaña.query.get_or_404(campaign_id)
    sched = request.form.get('scheduled_at') or request.form.get('schedule_date')
    if not sched:
        flash('Fecha de programación requerida', 'error')
        return redirect(url_for('admin.admin_campaigns'))
    try:
        if 'T' in sched:
            dt = datetime.strptime(sched, '%Y-%m-%dT%H:%M')
        else:
            dt = datetime.strptime(sched, '%Y-%m-%d %H:%M')
        # Si el cliente envía el offset de zona (en minutos), ajustarlo para almacenar UTC
        tz_offset = request.form.get('tz_offset')
        if tz_offset is not None and tz_offset != '':
            try:
                offset_min = int(tz_offset)
                dt = dt + timedelta(minutes=offset_min)
            except Exception:
                pass
        campaña.date = dt
        db.session.commit()
        flash('Campaña programada correctamente', 'success')
    except ValueError:
        flash('Formato de fecha inválido. Usa YYYY-MM-DDTHH:MM', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al programar la campaña: {e}', 'error')
    return redirect(url_for('admin.admin_campaigns'))


@admin_bp.route('/admin/reports')
def admin_reports():
    if session.get('logged_in') and session.get('role') == 'admin':
        # Estadísticas principales
        usuarios_count = Usuario.query.count()
        mensajes_count = Mensaje.query.count()
        grupos_count = Grupo.query.count()

        # Cambio relativo en los últimos 30 días vs los 30 días anteriores
        now = datetime.utcnow()
        last_30_start = now - timedelta(days=30)
        prev_30_start = now - timedelta(days=60)

        # Usuarios: no hay fecha de creación en Usuario, no es posible calcular cambio preciso
        usuarios_change = 0

        # Mensajes
        mensajes_recent = Mensaje.query.filter(Mensaje.fecha_envio >= last_30_start).count()
        mensajes_prev = Mensaje.query.filter(Mensaje.fecha_envio >= prev_30_start, Mensaje.fecha_envio < last_30_start).count()
        mensajes_change = 0
        try:
            if mensajes_prev > 0:
                mensajes_change = int(round((mensajes_recent - mensajes_prev) / float(mensajes_prev) * 100))
            else:
                mensajes_change = 100 if mensajes_recent > 0 else 0
        except Exception:
            mensajes_change = 0

        # Grupos: no hay fecha en Grupo
        grupos_change = 0

        # Actividad reciente: series para últimos 7 días (mensajes y campañas)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        labels = []
        messages_series = []
        campaigns_series = []
        for i in range(6, -1, -1):
            day_start = today - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            labels.append(day_start.strftime('%Y-%m-%d'))
            mcount = Mensaje.query.filter(Mensaje.fecha_envio >= day_start, Mensaje.fecha_envio < day_end).count()
            ccount = Campaña.query.filter(Campaña.date >= day_start, Campaña.date < day_end).count()
            messages_series.append(mcount)
            campaigns_series.append(ccount)

        # Últimas notificaciones/actividades (mezcla de mensajes y campañas)
        mensajes = Mensaje.query.order_by(Mensaje.fecha_envio.desc()).limit(6).all()
        campañas = Campaña.query.order_by(Campaña.date.desc()).limit(6).all()
        latest_notifications = []
        for m in mensajes:
            latest_notifications.append({'title': m.asunto or 'Mensaje', 'created_at': m.fecha_envio})
        for c in campañas:
            try:
                is_active = getattr(c, 'active', True)
            except Exception:
                is_active = True
            if not is_active:
                continue
            latest_notifications.append({'title': c.name or 'Campaña', 'created_at': c.date})
        latest_notifications = sorted(latest_notifications, key=lambda x: x.get('created_at') or datetime.utcnow(), reverse=True)[:6]

        return render_template('admin/admin_reports.html', admin_user=session.get('username'), usuarios_count=usuarios_count, mensajes_count=mensajes_count, grupos_count=grupos_count, usuarios_change=usuarios_change, mensajes_change=mensajes_change, grupos_change=grupos_change, latest_notifications=latest_notifications, activity_labels=labels, activity_messages=messages_series, activity_campaigns=campaigns_series)
    flash("Debe iniciar sesión como administrador", "error")
    return redirect(url_for('main.login'))


@admin_bp.route('/admin/settings', methods=['GET'])
@require_admin
def admin_settings():
    settings = Settings.query.first()
    return render_template('admin/admin_settings.html', settings=settings, admin_user=session.get('username'), support_email=(settings.support_email if settings else 'etecsa.ayuda@nauta.com.cu'), year=datetime.utcnow().year)


@admin_bp.route('/admin/settings/site', methods=['POST'], endpoint='admin_settings_site')
@require_admin
def admin_settings_site():
    settings = Settings.query.first()
    system_name = (request.form.get('siteName') or request.form.get('systemName') or request.form.get('system_name') or '').strip()
    support_email = (request.form.get('supportEmail') or request.form.get('support_email') or '').strip()
    default_page = (request.form.get('defaultPage') or request.form.get('default_page') or 'home').strip()
    try:
        max_concurrent = int(request.form.get('maxConcurrent') or request.form.get('max_concurrent') or 5)
        if max_concurrent < 1:
            max_concurrent = 1
    except Exception:
        max_concurrent = 5

    if not settings:
        settings = Settings()
        db.session.add(settings)

    settings.system_name = system_name or settings.system_name or 'Mensajería Masiva'
    settings.support_email = support_email or settings.support_email or 'etecsa.ayuda@nauta.com.cu'
    settings.default_page = default_page or settings.default_page or 'home'
    settings.max_concurrent = max_concurrent
    settings.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        flash('Ajustes del sitio guardados correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar ajustes del sitio: {e}', 'error')
    return redirect(url_for('admin.admin_settings'))


@admin_bp.route('/admin/settings/maintenance', methods=['POST'], endpoint='admin_settings_maintenance')
@require_admin
def admin_settings_maintenance():
    settings = Settings.query.first()
    maintenance = True if request.form.get('maintenance') in ('on', 'true', '1') else False
    maintenance_message = (request.form.get('maintenanceMessage') or request.form.get('maintenance_message') or '').strip()
    if not settings:
        settings = Settings()
        db.session.add(settings)
    settings.maintenance = maintenance
    settings.maintenance_message = maintenance_message
    settings.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        flash('Ajustes de mantenimiento guardados correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar ajustes de mantenimiento: {e}', 'error')
    return redirect(url_for('admin.admin_settings'))
