import sqlite3


# ==================================
# DATABASE CLASS
# ==================================

class Database:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # USERS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    balance REAL DEFAULT 3.5,
                    language TEXT DEFAULT 'es',
                    joined_group BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP
                )
            """)

            # TRANSACTIONS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    effect TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # GENERATED IMAGES
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    effect TEXT,
                    image_path TEXT,
                    prompt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    # ================= USERS =================

    def get_user(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            return cursor.fetchone()

    def create_user(self, user_id, username, first_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users
                (user_id, username, first_name, balance, joined_group)
                VALUES (?, ?, ?, 3.5, 0)
            """, (user_id, username, first_name))
            conn.commit()

    def update_last_active(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()

    # ================= BALANCE =================

    def get_balance(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT balance FROM users WHERE user_id = ?", (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def update_balance(self, user_id, amount):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET balance = balance + ?
                WHERE user_id = ?
            """, (amount, user_id))

            cursor.execute("""
                INSERT INTO transactions (user_id, amount, status)
                VALUES (?, ?, ?)
            """, (
                user_id,
                amount,
                "completed" if amount < 0 else "purchase"
            ))

            conn.commit()

            return self.get_balance(user_id)

    # ================= GROUP =================

    def set_joined_group(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET joined_group = 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()

    def has_joined_group(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT joined_group FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    # ================= LANGUAGE =================

    def set_language(self, user_id, language):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET language = ? WHERE user_id = ?",
                (language, user_id)
            )
            conn.commit()

    def get_language(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT language FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else "es"

    # ================= IMAGES =================

    def save_generated_image(self, user_id, effect, image_path, prompt=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO generated_images
                (user_id, effect, image_path, prompt)
                VALUES (?, ?, ?, ?)
            """, (user_id, effect, image_path, prompt))
            conn.commit()
            return cursor.lastrowid

    def get_user_images(self, user_id, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM generated_images
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            return cursor.fetchall()


# ==================================
# GLOBAL INSTANCE (IMPORTABLE)
# ==================================

db = Database()