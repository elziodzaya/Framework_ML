from utils.supabase_client import get_supabase
import pandas as pd
from tempfile import NamedTemporaryFile

supabase = get_supabase()

def get_total_users():
    response = supabase.table("users").select("id", count='exact').execute()
    return response.count

def get_all_users():
    response = supabase.table("users").select("*", count='exact').execute()
    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame()

def add_user(username, name, email, phone, password, role):
    existing = supabase.table("users").select("*").eq("username", username).execute()
    if existing.data:
        return False
    supabase.table("users").insert({
        "username": username,
        "name": name,
        "email": email,
        "phone": phone,
        "password": password,
        "role": role,
        "is_active": True
    }).execute()
    return True

def update_user(username, name, email, phone, role):
    supabase.table("users").update({
        "name": name,
        "email": email,
        "phone": phone,
        "role": role
    }).eq("username", username).execute()

def delete_user(username):
    supabase.table("users").delete().eq("username", username).execute()

def is_valid_email(email):
    return "@" in email and "." in email

def export_users():
    response = supabase.table("users").select("*").execute()
    if not response.data:
        return None
    df = pd.DataFrame(response.data)
    temp = NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp.name, index=False)
    return temp.name
