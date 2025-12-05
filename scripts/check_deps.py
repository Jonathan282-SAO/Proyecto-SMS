import sys
import platform

print("Python:", platform.python_version())

try:
    import flask
    import flask_sqlalchemy
    import werkzeug
    print("Dependencias: OK (flask, flask_sqlalchemy, werkzeug)")
except Exception as e:
    print("Error importando dependencias:", e)
    sys.exit(2)

print("Script de verificación finalizado.")
