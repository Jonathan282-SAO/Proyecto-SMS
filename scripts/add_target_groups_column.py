"""
Script ligero para SQLite: añade la columna `target_groups` a la tabla de campañas si falta.

Uso (desde la raíz del proyecto):
  python .\scripts\add_target_groups_column.py

Notas:
- Hace backup automático del fichero `app.db` (crea `app.db.bak`) antes de alterar.
- Soporta varios nombres comunes de la tabla: 'campaña', 'campana', 'campania'.
"""
import sqlite3
import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_PATHS = [ROOT / 'app.db', ROOT / 'instance' / 'app.db', ROOT / 'database.db']

def resolve_db_candidate(arg=None):
    # If user passed a path, prefer it
    if arg:
        p = Path(arg)
        if not p.is_absolute():
            p = Path.cwd() / p
        return p
    return None

def find_db():
    for p in DB_PATHS:
        if p.exists():
            return p
    return None

def main():
    # allow passing DB path as first arg
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    chosen = resolve_db_candidate(arg)
    if chosen and chosen.exists():
        dbfile = chosen
    else:
        dbfile = find_db()
    if not dbfile:
        print('No se encontró app.db en rutas conocidas. Coloca la base de datos en la raíz o en instance/.')
        sys.exit(1)

    print(f'Usando archivo de BD: {dbfile}')
    # backup
    bak = dbfile.with_suffix(dbfile.suffix + '.bak')
    try:
        shutil.copy(dbfile, bak)
        print(f'Backup creado: {bak}')
    except Exception as e:
        print(f'No se pudo crear backup: {e}. Continuando con precaución.')

    conn = sqlite3.connect(str(dbfile))
    cur = conn.cursor()

    tried_tables = ['campaña', 'campana', 'campania', 'campania']
    found_any = False
    for tbl in tried_tables:
        try:
            cur.execute(f"PRAGMA table_info('{tbl}')")
            rows = cur.fetchall()
        except Exception:
            rows = []
        if rows:
            found_any = True
            cols = [r[1] for r in rows]
            if 'target_groups' in cols:
                print(f"La tabla '{tbl}' ya tiene la columna 'target_groups'. Nada que hacer.")
                conn.close()
                return
            else:
                try:
                    cur.execute(f'ALTER TABLE "{tbl}" ADD COLUMN target_groups TEXT')
                    conn.commit()
                    print(f"Columna 'target_groups' añadida correctamente a la tabla '{tbl}'.")
                    conn.close()
                    return
                except Exception as e:
                    print(f"Error al alterar la tabla '{tbl}': {e}")
                    conn.close()
                    sys.exit(1)

    conn.close()
    if not found_any:
        print('No se encontró la tabla Campaña con los nombres probados. Revisa el esquema de la base de datos.')
        sys.exit(1)

if __name__ == '__main__':
    main()
