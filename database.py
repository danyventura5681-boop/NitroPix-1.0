import sqlite3
import os

DB_FILE = "users.db"


# ===============================
# CONEXIÓN
# ===============================
def get_connection():
    return sqlite3.connect(DB_FILE)


# ===============================
# CREAR TABLA
# ===============================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            credits INTEGER DEFAULT 5
        )
    """)

    conn.commit()
    conn.close()


# ===============================
# OBTENER USUARIO
# (lo crea automáticamente si no existe)
# ===============================
def get_user(user_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, credits FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()

    # ✅ Crear usuario automáticamente
    if not row:
        cursor.execute(
            "INSERT INTO users (user_id, credits) VALUES (?, ?)",
            (user_id, 5)
        )
        conn.commit()

        cursor.execute(
            "SELECT user_id, credits FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()

    conn.close()

    return {
        "user_id": row[0],
        "credits": row[1]
    }


# ===============================
# AGREGAR CRÉDITOS
# ===============================
def add_credits(user_id: int, amount: int = 1):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET credits = credits + ?
        WHERE user_id = ?
    """, (amount, user_id))

    conn.commit()
    conn.close()


# ===============================
# RESTAR CRÉDITOS (FUNCIÓN REAL)
# ===============================
def deduct_diamond(user_id: int, amount: int = 1):

    user = get_user(user_id)

    if not user:
        return False

    if user["credits"] < amount:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET credits = credits - ?
        WHERE user_id = ?
    """, (amount, user_id))

    conn.commit()
    conn.close()

    return True


# ===============================
# ✅ ALIAS PARA COMPATIBILIDAD
# (usado por effects.py)
# ===============================
def remove_credits(user_id: int, amount: int = 1):
    return deduct_diamond(user_id, amount)