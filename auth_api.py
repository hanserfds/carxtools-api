from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import string
from datetime import datetime

from database import get_connection

app = FastAPI()


# -------------------------------
# CREAR TABLAS AL INICIAR
# -------------------------------

@app.on_event("startup")
def startup():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuario (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT NOT NULL UNIQUE,
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


# -------------------------------
# MODELOS
# -------------------------------

class LoginData(BaseModel):
    usuario: str
    contrasena: str


class RegisterData(BaseModel):
    nombre: str
    usuario: str
    contrasena: str


class ActivateData(BaseModel):
    codigo: str


# -------------------------------
# UTILIDADES
# -------------------------------

def random_str(n: int) -> str:
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=n)
    )


# -------------------------------
# LOGIN
# -------------------------------

@app.post("/login")
def login(data: LoginData):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id_user, nombre FROM usuario WHERE usuario=? AND contrasena=?",
        (data.usuario, data.contrasena)
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {
        "mensaje": "Login exitoso",
        "id_user": user[0],
        "nombre": user[1]
    }


# -------------------------------
# REGISTRAR USUARIO
# -------------------------------

@app.post("/register")
def register(data: RegisterData):
    conn = get_connection()
    cur = conn.cursor()

    # Verificar si el usuario ya existe
    cur.execute(
        "SELECT id_user FROM usuario WHERE usuario=?",
        (data.usuario,)
    )
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    # Insertar usuario
    cur.execute(
        "INSERT INTO usuario (nombre, usuario, contrasena) VALUES (?, ?, ?)",
        (data.nombre, data.usuario, data.contrasena)
    )

    conn.commit()
    conn.close()

    return {
        "mensaje": "Usuario creado correctamente"
    }


# -------------------------------
# ACTIVAR POR CÓDIGO (UNA SOLA VEZ)
# -------------------------------

@app.post("/activate")
def activate(data: ActivateData):
    conn = get_connection()
    cur = conn.cursor()

    # 1️⃣ Verificar código válido y no usado
    cur.execute(
        "SELECT id FROM codigos WHERE codigo=? AND usado=0",
        (data.codigo,)
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="Código inválido o ya usado")

    # 2️⃣ Generar credenciales
    usuario = "cxt_" + random_str(8)
    contrasena = random_str(16)

    # 3️⃣ Marcar código como usado
    cur.execute(
        "UPDATE codigos SET usado=1, usado_en=? WHERE id=?",
        (datetime.now().isoformat(), row[0])
    )

    conn.commit()
    conn.close()

    # 4️⃣ DEVOLVER (SOLO ESTA VEZ)
    return {
        "usuario": usuario,
        "contrasena": contrasena
    }
