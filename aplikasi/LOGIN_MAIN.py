# LOGIN_MAIN.py

import os

# --- Hapus __pycache__ jika ada ---
pycache_path = os.path.join("utils", "__pycache__")
if os.path.exists(pycache_path):
    import shutil
    shutil.rmtree(pycache_path, ignore_errors=True)

# --- Nonaktifkan monitoring __pycache__ jika Streamlit mendukung ---
try:
    import streamlit.runtime.runtime as runtime

    watcher = runtime.get_instance()._file_watcher
    if watcher and hasattr(watcher, "_watched_paths"):
        watcher._watched_paths = {
            path: info
            for path, info in watcher._watched_paths.items()
            if "__pycache__" not in path
        }
except Exception:
    pass  # aman diabaikan jika versi tidak mendukung


import streamlit as st
import time
from utils.auth_utils import register_user, login_user, activate_user
from utils.email_utils import send_activation_email

# create_users_table()

# ==== CEGAH AKSES HALAMAN LOGIN JIKA SUDAH LOGIN ====
if st.session_state.get("logged_in"):
    st.switch_page("pages/DASHBOARD.py")
    st.stop()

# ==== AKTIVASI AKUN ====


params = st.query_params
if "token" in params:
    token = params["token"]
    if activate_user(token):
        st.success("✅ Akun berhasil diaktifkan! Anda akan diarahkan ke halaman login...")

        st.markdown("""
            <meta http-equiv="refresh" content="3; url=/" />
        """, unsafe_allow_html=True)

        st.stop()
    else:
        st.error("❌ Token tidak valid atau sudah dipakai.")
        st.stop()


# ==== MODE LOGIN / REGISTER ====
if "mode" not in st.session_state:
    st.session_state.mode = "login"

def switch(mode):
    st.session_state.mode = mode
    st.rerun()

# ==== HALAMAN LOGIN ====
if st.session_state.mode == "login":
    st.header("🔐 Login")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    
    if st.button("Login"):
        role = login_user(uname, pwd)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = uname
            st.session_state.role = role
            st.success(f"Berhasil login sebagai **{role}**.")
            st.switch_page("pages/DASHBOARD.py")
        else:
            st.error("Username/password salah atau akun belum aktif.")
    
    st.write("")
    if st.button("➕ Create Akun"):
        switch("register")

# ==== HALAMAN REGISTER ====
elif st.session_state.mode == "register":
    st.header("📝 Registrasi")
    name = st.text_input("Nama Lengkap")
    email = st.text_input("Email")
    phone = st.text_input("No. Telepon")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    confirm = st.text_input("Konfirmasi Password", type="password")

    if st.button("Register"):
        if not (name and email and phone and uname and pwd):
            st.warning("Mohon isi semua kolom.")
        elif pwd != confirm:
            st.error("Password tidak cocok.")
        else:
            token = register_user(name, email, phone, uname, pwd)
            if token:
                send_activation_email(email, token)
                st.success("Pendaftaran berhasil! Cek email untuk aktivasi.")
                switch("login")
            else:
                st.error("Email atau Username sudah dipakai.")

    st.write("")
    if st.button("🔙 Kembali ke Login"):
        switch("login")
