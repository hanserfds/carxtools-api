import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuario (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT NOT NULL,
    contrasena TEXT NOT NULL
)
""")

cursor.execute(
    "INSERT INTO usuario (nombre, usuario, contrasena) VALUES (?, ?, ?)",
    ("Juan Perez", "juan", "1234")
)

conn.commit()
conn.close()

print("Base de datos creada")
