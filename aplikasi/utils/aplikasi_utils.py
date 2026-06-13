import streamlit as st
import pandas as pd
import joblib
import os
import io
from datetime import datetime

# Ambil rentang nilai min dan max dari dataset, dengan fallback jika gagal
def get_input_range(data_input, fitur, target_col=None, fallback=(0.0, 10000.0)):
    if data_input is not None and fitur != target_col:
        try:
            min_val = float(data_input[fitur].min())
            max_val = float(data_input[fitur].max())
            return min_val, max_val
        except Exception:
            pass
    return fallback

# Encode data input manual dan konversi ke DataFrame numerik
def process_manual_input(input_data, fitur_model, cat_cols, label_encoders):
    input_df = pd.DataFrame([input_data])
    for col in cat_cols:
        input_df[col] = input_df[col].map(label_encoders[col])
    for col in input_df.columns:
        try:
            input_df[col] = pd.to_numeric(input_df[col])
        except Exception:
            pass
    return input_df

# Siapkan data prediksi (dari file upload)
def prepare_data_for_prediction(df, fitur_model, cat_cols, label_encoders):
    df = df[fitur_model]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].map(label_encoders[col])
    return df

# Tambahkan hasil prediksi dan keterangannya ke DataFrame
def generate_result(df_pred, model, target_col=None, data_input=None):
    prediksi = model.predict(df_pred)
    keterangan_map = dict(enumerate(data_input[target_col].unique())) if target_col and data_input is not None else None
    df_pred["Prediksi"] = prediksi
    df_pred["Keterangan"] = df_pred["Prediksi"].apply(lambda x: keterangan_map.get(x, x) if keterangan_map else x)
    return df_pred

# Simpan hasil prediksi manual ke session
def save_manual_prediction_to_session(input_data, pred, keterangan):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"Timestamp": timestamp, "Prediksi": pred, "Keterangan": keterangan}
    entry.update(input_data)

    if "manual_history" not in st.session_state:
        st.session_state.manual_history = []

    st.session_state.manual_history.append(entry)

# Unduh riwayat prediksi manual (session) sebagai CSV
def download_manual_history_csv():
    df = pd.DataFrame(st.session_state.manual_history)
    return df.to_csv(index=False).encode("utf-8")

# Unduh riwayat prediksi manual (session) sebagai Excel
def download_manual_history_excel():
    df = pd.DataFrame(st.session_state.manual_history)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output
