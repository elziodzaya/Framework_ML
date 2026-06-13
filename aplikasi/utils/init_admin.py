import os
import sqlite3
from auth_utils import create_users_table, hash_password

# Jalankan create_users_table untuk memastikan tabel dibuat
create_users_table()

def add_admin_if_not_exists():
    DB_PATH = os.path.join("database", "users.db")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Cek apakah admin sudah ada
    c.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    if not c.fetchone():
        print("Menambahkan admin...")

        # Tambah admin secara langsung dengan SQL + password di-hash
        c.execute('''
            INSERT INTO users (name, email, phone, username, password, is_active, activation_token, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Administrator",                # name
            "njaya7585@gmail.com",          # email
            "081234567890",                 # phone
            "admin",                        # username
            hash_password("admin123"),      # hashed password
            1,                              # is_active (langsung aktif)
            None,                           # activation_token
            "admin"                         # role
        ))
        conn.commit()
        print("✅ Admin berhasil ditambahkan.")
    else:
        print("ℹ️ Admin sudah terdaftar.")
    conn.close()

add_admin_if_not_exists()
