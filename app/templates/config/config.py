# config.py
class Config:
    SECRET_KEY = "TuClaveSecretaMuySegura"  # Cambia esta clave en producción
    SQLALCHEMY_DATABASE_URI = "sqlite:///mensajeria.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
