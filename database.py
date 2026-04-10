import sqlite3
import os

DB_FILE = "vault.db"

def init_db():
    """Inicializa la base de datos SQLite y las tablas si no existen."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabla de configuración para la contraseña maestra (solo guarda Hash y Salt)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY,
            master_hash BLOB NOT NULL,
            salt BLOB NOT NULL
        )
    ''')
    
    # Tabla del baúl (TODO está cifrado como BLOB, excepto el ID)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enc_service BLOB NOT NULL,
            enc_username BLOB NOT NULL,
            enc_password BLOB NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def is_first_run() -> bool:
    """Comprueba si existe una contraseña maestra configurada."""
    if not os.path.exists(DB_FILE):
        return True
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Intenta obtener la tabla de config por si el archivo existe pero está vacío
    try:
        cursor.execute("SELECT COUNT(*) FROM config")
        count = cursor.fetchone()[0]
        conn.close()
        return count == 0
    except sqlite3.OperationalError:
        conn.close()
        return True

def setup_master_password(master_hash: bytes, salt: bytes):
    """Guarda el hash y el salt inicial en la base de datos."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO config (id, master_hash, salt) VALUES (1, ?, ?)", (master_hash, salt))
    conn.commit()
    conn.close()

def get_master_data():
    """Recupera el hash y el salt para la validación del login."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT master_hash, salt FROM config WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row

def add_entry(enc_service: bytes, enc_username: bytes, enc_password: bytes):
    """Añade una nueva cuenta cifrada al baúl."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vault (enc_service, enc_username, enc_password) VALUES (?, ?, ?)",
        (enc_service, enc_username, enc_password)
    )
    conn.commit()
    conn.close()

def get_all_entries() -> list:
    """Obtiene todas las filas cifradas del baúl."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, enc_service, enc_username, enc_password FROM vault")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_entry(entry_id: int, enc_service: bytes, enc_username: bytes, enc_password: bytes):
    """Actualiza un registro específico cifrado."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE vault SET enc_service = ?, enc_username = ?, enc_password = ? WHERE id = ?",
        (enc_service, enc_username, enc_password, entry_id)
    )
    conn.commit()
    conn.close()

def delete_entry(entry_id: int):
    """Elimina una cuenta del baúl."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vault WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_all_entries_for_export(self):
    self.cursor.execute("SELECT service, username, password FROM passwords")
    return self.cursor.fetchall()