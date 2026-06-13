import streamlit as st
import os
import base64
from utils.utils_manajuser import (
    get_total_users, get_all_users, add_user, update_user,
    delete_user, export_users, is_valid_email
)
import pandas as pd
from utils.footer import render_footer

# === CONFIG ===
st.set_page_config(page_title="Dashboard", layout="wide")



# ========== Inisialisasi session state ==========
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = "Guest"
if "role" not in st.session_state:
    st.session_state["role"] = "user"

username = st.session_state["username"]
role = st.session_state["role"]

# # === CEK LOGIN ===
# if not st.session_state.get("logged_in"):
#     st.warning("Silakan login terlebih dahulu.")
#     st.stop()

# === SIDEBAR ===
st.sidebar.title("👤 User")
username = st.session_state.get("username", "Guest")
role = st.session_state.get("role", "user")
st.sidebar.markdown(f"**Username:** `{username}`")
st.sidebar.markdown(f"**Role:** `{role}`")


st.sidebar.markdown(f"**Total Users:** `{get_total_users()}` 👥")

# Tombol admin panel toggle
show_admin = False
if role == "admin":
    show_admin = st.sidebar.checkbox("🛠 Admin Panel")

# Tombol logout
if st.sidebar.button("🔓 Logout"):
    for key in ["logged_in", "username", "role"]:
        st.session_state.pop(key, None)
    st.success("Berhasil logout.")
    st.switch_page("LOGIN_MAIN.py")

# === HALAMAN UTAMA ===
if show_admin:
    st.title("👤 Admin Panel - Manajemen Pengguna")

    # Search
    query = st.text_input("🔍 Cari berdasarkan username/nama/email")
    df = get_all_users()

    if query:
        df = df[df.apply(lambda row: query.lower() in row.astype(str).str.lower().to_string(), axis=1)]

    st.dataframe(df, use_container_width=True)

    # Tambah user
    st.markdown("---")
    st.subheader("➕ Tambah Pengguna Baru")
    with st.form("form_add"):
        col1, col2, col3 = st.columns(3)
        with col1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
        with col2:
            name = st.text_input("Nama Lengkap")
            phone = st.text_input("No. Telepon")
        with col3:
            email = st.text_input("Email")
            role = st.selectbox("Role", ["user", "admin"])

        submit = st.form_submit_button("Tambah")
        if submit:
            if not (username and password and name and email):
                st.warning("Mohon isi semua kolom yang dibutuhkan.")
            elif not is_valid_email(email):
                st.error("Format email tidak valid.")
            elif add_user(username, name, email, phone, password, role):
                st.success(f"User '{username}' berhasil ditambahkan.")
            else:
                st.error("Username sudah digunakan.")

    # Edit/delete
    st.markdown("---")
    st.subheader("✏️ Edit atau Hapus Pengguna")
    user_list = df["username"].tolist()
    selected_user = st.selectbox("Pilih Username", user_list)
    if selected_user:
        user_row = df[df.username == selected_user].iloc[0]
        with st.form("form_edit"):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Nama", user_row.name)
            with col2:
                email = st.text_input("Email", user_row.email)
            with col3:
                phone = st.text_input("Telepon", user_row.phone)
            role = st.selectbox("Role", ["user", "admin"], index=["user", "admin"].index(user_row.role))
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.form_submit_button("Simpan Perubahan"):
                    if not is_valid_email(email):
                        st.error("Format email tidak valid.")
                    else:
                        update_user(selected_user, name, email, phone, role)
                        st.success("Perubahan disimpan.")
            with action_col2:
                if st.form_submit_button("❌ Hapus Pengguna"):
                    delete_user(selected_user)
                    st.success("Pengguna dihapus.")

    # Export Excel
    st.markdown("---")
    with open(export_users(), "rb") as f:
        st.download_button("📁 Download Data Pengguna", f, file_name="data_pengguna.xlsx")

else:
    # Tampilan dashboard biasa
    st.markdown('<div style="text-align:center;"><h1>DATA SCIENCE FRAMEWORK</h1></div>', unsafe_allow_html=True)
    # === Path ke gambar ===
    root_path = os.path.dirname(os.path.dirname(__file__))
    image_path = os.path.join(root_path, 'gambar', 'home.jpg')
    


    # Tampilkan gambar jika ada
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
            encoded = base64.b64encode(img_bytes).decode()
            st.markdown(
                f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{encoded}" width="500"/></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("Gambar home.jpg tidak ditemukan.")
    st.markdown("""
        <div style="text-align: center;">
            <strong>This application functions as a tool for creating models and applications based on machine learning.</strong><br>
            By using this application, you can perform data analysis and visualization more quickly and efficiently, as well as build machine learning models with classification techniques.<br>
            <a href="https://www.youtube.com/watch?v=J0Z1SKt0kBE&t=1761s" target="_blank">📺 Application Demo</a>
        </div>
    """, unsafe_allow_html=True)
# Footer
render_footer()
