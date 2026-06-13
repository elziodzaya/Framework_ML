import streamlit as st
import os
import base64

from utils.footer import render_footer

# === CONFIG ===
st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

# Judul Dashboard
st.markdown(
    '<div style="text-align:center;"><h1>DATA SCIENCE FRAMEWORK</h1></div>',
    unsafe_allow_html=True
)

# Path gambar

image_path = os.path.join('gambar', 'home.jpg')

# Tampilkan gambar jika ada
if os.path.exists(image_path):
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()
        encoded = base64.b64encode(img_bytes).decode()

    st.markdown(
        f'''
        <div style="text-align:center;">
            <img src="data:image/jpeg;base64,{encoded}" width="500">
        </div>
        ''',
        unsafe_allow_html=True
    )
else:
    st.info("Gambar home.jpg tidak ditemukan.")

# Deskripsi aplikasi
st.markdown("""
<div style="text-align:center;">
    <strong>
    This application functions as a tool for creating models and applications based on machine learning.
    </strong>
    <br><br>

    By using this application, you can perform data analysis and visualization more quickly and efficiently,
    as well as build machine learning models with classification techniques.
    <br><br>

    <a href="https://www.youtube.com/watch?v=J0Z1SKt0kBE&t=1761s" target="_blank">
        📺 Application Demo
    </a>
</div>
""", unsafe_allow_html=True)

# Footer
render_footer()
