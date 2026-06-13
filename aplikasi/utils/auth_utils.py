import uuid
import hashlib
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import dateutil.parser  
from utils.supabase_client import get_supabase

supabase = get_supabase()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, phone, username, password):
    # Generate token unik
    token = str(uuid.uuid4())

    # Cek apakah email atau username sudah dipakai
    existing_email = supabase.table("users").select("*").eq("email", email).execute()
    existing_username = supabase.table("users").select("*").eq("username", username).execute()

    if existing_email.data or existing_username.data:
        return None  # Username/email sudah ada


    hashed = hash_password(password)

    # Insert user
    supabase.table("users").insert({
        "name": name,
        "email": email,
        "phone": phone,
        "username": username,
        "password": hashed,
        "token": token
    }).execute()

    return token  # untuk dikirim via email


def activate_user(token):
    try:
        # Ambil user berdasarkan token
        response = supabase.table("users").select("*").eq("token", token).execute()
        if not response.data:
            return False  # Token tidak ditemukan

        user = response.data[0]

        # Update user: aktifkan dan hapus token (tanpa cek waktu)
        supabase.table("users").update({
            "is_active": True,
            "token": None,
        }).eq("id", user["id"]).execute()

        return True

    except Exception as e:
        # Bisa log error jika perlu
        return False


def login_user(username, password):
    hashed = hash_password(password)
    result = supabase.table("users").select("*").eq("username", username).eq("password", hashed).execute()

    if result.data and result.data[0]["is_active"]:
        return result.data[0]["role"]  # atau kembalikan objek user
    return None
