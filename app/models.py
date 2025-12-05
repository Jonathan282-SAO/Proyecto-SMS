# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# Asociación many-to-many entre usuarios y grupos
user_grupo = db.Table(
    'user_grupo',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('grupo_id', db.Integer, db.ForeignKey('grupo.id'), primary_key=True)
)


class Usuario(db.Model):  # type: ignore
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


class Settings(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(200), nullable=True)
    support_email = db.Column(db.String(200), nullable=True)
    default_page = db.Column(db.String(50), nullable=True)
    max_concurrent = db.Column(db.Integer, default=5)
    maintenance = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Campaña(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    # grupos destinatarios: almacenados como JSON list of group ids (opcional)
    target_groups = db.Column(db.Text, nullable=True)
    # prioridad: 'alta', 'media', 'baja' (opcional)
    priority = db.Column(db.String(10), nullable=True, default='baja')
    # bandera para activar/desactivar la campaña (si la BD no tiene esta columna, usar el script en /scripts)
    # Por defecto las campañas nuevas empiezan INACTIVAS; el administrador debe activarlas.
    active = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Grupo(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    # relación con usuarios (muchos a muchos)
    usuarios = db.relationship('Usuario', secondary=user_grupo, backref=db.backref('grupos', lazy=True), lazy=True)


class Mensaje(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    asunto = db.Column(db.String(150))
    contenido = db.Column(db.Text)
    modalidad = db.Column(db.String(50))
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)

    grupo = db.relationship('Grupo', backref=db.backref('mensajes', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('mensajes', lazy=True))
