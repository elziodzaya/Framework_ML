import pandas as pd
import streamlit as st
import uuid
import joblib

def check_session_keys(keys: list, warning_message: str = None) -> bool:
    """Cek apakah semua key tersedia di session_state"""
    missing_keys = [k for k in keys if k not in st.session_state]
    if missing_keys:
        if warning_message:
            st.warning(warning_message)
        return False
    return True


def upload_data(file, session_key="df"):
    """
    Mengunggah file CSV/XLSX dan menyimpannya ke dalam session_state.
    """
    if file is None:
        return

    # Gunakan nama file + ukuran sebagai id sederhana untuk mencegah re-upload
    file_id = f"{file.name}_{file.size}"

    # Jika file belum diproses sebelumnya
    if st.session_state.get(f"{session_key}_id") != file_id:
        try:
            if file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)

            st.session_state[session_key] = df.copy()
            st.session_state[f"{session_key}_id"] = file_id  # Simpan ID file

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")


def upload_model(file, session_key="trained_model", fitur_key="model_features"):
    """
    Mengunggah model .joblib dan menyimpannya ke session_state.
    - file: file dari st.file_uploader
    - session_key: key session_state untuk menyimpan model
    - fitur_key: key untuk menyimpan fitur dari model (jika tersedia)
    """
    if file is None:
        if session_key in st.session_state:
            del st.session_state[session_key]
        return

    try:
        model = joblib.load(file)
        st.session_state[session_key] = model

        # Simpan fitur jika tersedia
        if hasattr(model, 'feature_names_in_'):
            st.session_state[fitur_key] = list(model.feature_names_in_)
        else:
            st.session_state[fitur_key] = []

        st.success("✅ Model berhasil dimuat.")
       
    except Exception as e:
        st.error(f"❌ Gagal memuat model: {e}")



def reset_data():
    """
    Menghapus semua session_state terkait proses prediksi & upload.
    Tetap mempertahankan kompatibilitas lintas halaman.
    """
    keys_to_clear = [
        "df", "trained_model", "X_test", "y_test", "is_multiclass",
        "label_data", "predict_data", "model_features",
        "flag_upload_selesai", "show_reset_button",
        "model_upload_key", "prediksi_csv", "data_label", "form_manual"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Reset file_uploader
    st.session_state["upload_key"] = str(uuid.uuid4())

    # Muat ulang halaman
    st.rerun()