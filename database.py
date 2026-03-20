import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

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
            credits INTEGER DEFAULT 5,
            language TEXT DEFAULT 'en',
            last_daily TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ==============================
# HELPERS
# ==============================
def row_to_dict(row):
    return dict(row) if row else None


# ==============================
# USUARIO
# ==============================
def get_user(user_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    # crear usuario automático
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        conn.commit()

        cursor.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        )
        user = cursor.fetchone()

    conn.close()
    return row_to_dict(user)


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


def deduct_diamond(user_id: int, amount: int = 1):

    user = get_user(user_id)

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


# ✅ alias para effects.py
def remove_credits(user_id: int, amount: int = 1):
    return deduct_diamond(user_id, amount)


# ✅ alias para daily.py
def add_diamonds(user_id: int, amount: int):
    add_credits(user_id, amount)


def get_credits(user_id: int):
    return get_user(user_id)["credits"]


# ==============================
# LANGUAGE
# ==============================
def set_language(user_id: int, lang: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET language = ?
        WHERE user_id = ?
    """, (lang, user_id))

    conn.commit()
    conn.close()


# ==============================
# DAILY REWARD
# ==============================
def can_claim_daily(user_id: int):

    user = get_user(user_id)
    last_claim = user["last_daily"]

    if not last_claim:
        return True

    last_date = datetime.fromisoformat(last_claim)

    return datetime.utcnow() - last_date >= timedelta(hours=24)


def set_daily_claimed(user_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET last_daily = ?
        WHERE user_id = ?
    """, (datetime.utcnow().isoformat(), user_id))

    conn.commit()
    conn.close()