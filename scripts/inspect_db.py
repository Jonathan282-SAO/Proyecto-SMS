# scripts/inspect_db.py
# Inspecciona un fichero SQLite y muestra tablas y columnas.
# Uso: python .\scripts\inspect_db.py [ruta_a_db]

import sqlite3
import sys
from pathlib import Path

def inspect(dbpath):
    p = Path(dbpath)
    if not p.exists():
        print(f"ERROR: no existe {p}")
        return 2
    print(f"Usando BD: {p}\n")
    conn = sqlite3.connect(str(p))
    cur = conn.cursor()
    try:
        tbls = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        tbls = [t[0] for t in tbls]
        print("Tablas encontradas:")
        for t in tbls:
            print('  -', t)
        print('\n')
        # nombres posibles
        candidates = ['campaña','campana','campania','Campaña','campana']
        for name in candidates:
            if name in tbls:
                print(f"Info de tabla '{name}':")
                cols = cur.execute(f"PRAGMA table_info('{name}')").fetchall()
                print('  Columnas:', [c[1] for c in cols])
                # show sample rows and column types
                try:
                    sample = cur.execute(f"SELECT * FROM \"{name}\" LIMIT 5").fetchall()
                    print('  Muestras (hasta 5 filas):')
                    for row in sample:
                        print('   ', row)
                except Exception as e:
                    print('  No se pudieron leer filas:', e)
                print('\n')
        return 0
    finally:
        conn.close()

if __name__ == '__main__':
    db = sys.argv[1] if len(sys.argv) > 1 else 'app.db'
    sys.exit(inspect(db))
