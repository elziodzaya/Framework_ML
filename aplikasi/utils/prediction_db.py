import os
import sqlite3
import pandas as pd
import streamlit as st
from fpdf import FPDF
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "prediction_history.db")

print("Connecting to DB at:", os.path.abspath(DB_PATH))

# Pastikan folder database ada
db_folder = os.path.dirname(DB_PATH)
if not os.path.exists(db_folder):
    print(f"Folder {db_folder} tidak ada, membuat folder...")
    os.makedirs(db_folder)

def create_prediction_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT,
                input_data TEXT,
                prediction TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("Tabel prediction_history berhasil dibuat atau sudah ada.")
    except Exception as e:
        print("Error saat membuat tabel:", e)
        raise e

def insert_prediction_history(input_df, prediction):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        from datetime import datetime

        input_json = input_df.to_json(orient='records')
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO prediction_history (datetime, input_data, prediction) VALUES (?, ?, ?)",
            (now, input_json, str(prediction))
        )
        conn.commit()
        conn.close()
        print("Data prediksi berhasil disimpan.")
    except Exception as e:
        print("Error saat insert data prediksi:", e)
        raise e


def export_prediction_to_excel(df, predictions):
    df_copy = df.copy()
    df_copy['Prediksi'] = predictions.values if hasattr(predictions, 'values') else predictions
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_copy.to_excel(writer, index=False)
    data = output.getvalue()
    st.download_button("Download Excel", data, file_name="prediksi.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def export_prediction_to_pdf(df, predictions):
    # Contoh sederhana export ke PDF (bisa dikembangkan)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hasil Prediksi", ln=True, align="C")
    for i, row in df.iterrows():
        text = ", ".join([f"{col}: {row[col]}" for col in df.columns]) + f", Prediksi: {predictions[i]}"
        pdf.cell(200, 10, txt=text, ln=True)
    pdf_output = pdf.output(dest='S').encode('latin-1')
    st.download_button("Download PDF", pdf_output, file_name="prediksi.pdf", mime="application/pdf")
    
def generate_excel_bytes(df, predictions):
    df_copy = df.copy()
    df_copy['Prediksi'] = predictions.values if hasattr(predictions, 'values') else predictions
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_copy.to_excel(writer, index=False)
    return output.getvalue()

def generate_pdf_bytes(df, predictions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hasil Prediksi", ln=True, align="C")
    for i, row in df.iterrows():
        text = ", ".join([f"{col}: {row[col]}" for col in df.columns]) + f", Prediksi: {predictions[i]}"
        pdf.cell(200, 10, txt=text, ln=True)
    return pdf.output(dest='S').encode('latin-1')
