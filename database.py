import sqlite3
from pathlib import Path

DB_PATH = Path("nitropix.db")


# ==============================
# CONEXIÓN
# ==============================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# CREAR TABLAS
# ==============================

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


# Ejecutar al importar
init_db()


# ==============================
# USUARIOS
# ==============================

def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, credits) VALUES (?, ?)",
            (user_id, 5)
        )
        conn.commit()

        cursor.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        )
        user = cursor.fetchone()

    conn.close()
    return user


# ==============================
# CRÉDITOS
# ==============================

def add_credits(user_id: int, amount: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET credits = credits + ?
        WHERE user_id = ?
    """, (amount, user_id))

    conn.commit()
    conn.close()


def remove_credits(user_id: int, amount: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET credits = credits - ?
        WHERE user_id = ?
    """, (amount, user_id))

    conn.commit()
    conn.close()


def get_credits(user_id: int) -> int:
    user = get_user(user_id)
    return user["credits"]
# ==============================
# DEDUCT DIAMOND (FIX RENDER)
# ==============================

def deduct_diamond(user_id: int, amount: int = 1):
    """
    Resta diamantes/créditos al usuario
    """

    user = get_user(user_id)

    if not user:
        return False

    credits = user.get("credits", 0)

    if credits < amount:
        return False

    user["credits"] = credits - amount

    save_user(user_id, user)

    return True