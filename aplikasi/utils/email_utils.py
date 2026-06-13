import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Ganti dengan data kamu
SMTP_EMAIL = st.secrets["email"]["smtp_email"]
SMTP_APP_PASSWORD = st.secrets["email"]["smtp_password"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_activation_email(recipient_email, token):
    base_url = st.secrets["app"]["base_url"]
    activation_link = f"{base_url}/?token={token}"


    
    subject = "Aktivasi Akun Anda"
    body = f"""
    <h3>Selamat datang!</h3>
    <p>Silakan klik link di bawah ini untuk mengaktifkan akun Anda:</p>
    <a href="{activation_link}">{activation_link}</a>
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            server.send_message(msg)
            print("✅ Email berhasil dikirim.")
    except Exception as e:
        print(f"❌ Gagal mengirim email: {e}")
