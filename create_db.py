from database import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS usuario (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT NOT NULL,
    contrasena TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS codigos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    usado INTEGER DEFAULT 0,
    usado_en TEXT
)
""")

conn.commit()
conn.close()

print("Base de datos creada")
