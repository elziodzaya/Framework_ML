import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from utils.footer import render_footer
from utils.model_utils import (
    get_algoritma_list, train_model, evaluate_model, zip_model,
    tampilkan_distribusi, plot_confusion_matrix, plot_roc_curve
)
from utils.session_utils import upload_data, reset_data, check_session_keys
from utils.evaluation import generate_evaluation_pdf
from utils.ui_utils import render_centered_title

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Silakan login terlebih dahulu melalui halaman Login.")
    st.stop()

render_centered_title("🔧 MODEL TRAINING")
st.markdown("""
<div style="text-align: center;">
    Halaman ini berfungsi untuk melatih (membangun) model Machine Learning (pembelajaran pada mesin),
    dengan menggunakan algoritma (metode) yang sesuai dengan kebutuhan.
</div>
""", unsafe_allow_html=True)
st.divider()

if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = "uploader_1"

uploaded_file = st.file_uploader("Unggah Data CSV", type=["csv", "xlsx"], key=st.session_state["upload_key"])
upload_data(uploaded_file)

if uploaded_file and "df" in st.session_state:
    df = st.session_state["df"]
    st.success("✅ Data berhasil dimuat!")
    st.write("📄 Preview Data", df.head())
    st.write(f"DIMENSI DATA: {df.shape[0]} Baris X {df.shape[1]} Kolom")
    st.divider()

    tabs = st.tabs([
        "🎯 Target & Fitur", 
        "🔍 Split & Balancing", 
        "🚀 Pelatihan", 
        "📈 Evaluasi", 
        "💾 Simpan Model"
    ])

    with tabs[0]:
        all_columns = df.columns.tolist()
        target_column = st.selectbox("🎯 Pilih Kolom Target", options=all_columns)
        if target_column:
            feature_columns = [col for col in all_columns if col != target_column]
            selected_features = st.multiselect("🧩 Pilih Fitur", options=feature_columns, default=feature_columns)
            st.session_state['target_column'] = target_column
            st.session_state['selected_features'] = selected_features

    with tabs[1]:
        if 'selected_features' in st.session_state and 'target_column' in st.session_state:
            X = df[st.session_state['selected_features']]
            y = df[st.session_state['target_column']]

            tampilkan_distribusi(y, "Distribusi Kelas Sebelum Balancing")

            test_size = st.slider("Proporsi Data Uji", 0.1, 0.5, 0.2)
            random_state = st.number_input("Random State", value=42, step=1)
            method_balancing = st.selectbox("Metode Balancing", ["None", "SMOTE", "Random Undersampling"])

            if st.button("🔀 Split & Balance"):
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=random_state, stratify=y
                )

                if method_balancing == "SMOTE":
                    X_train, y_train = SMOTE(random_state=random_state).fit_resample(X_train, y_train)
                    st.success("✅ SMOTE berhasil diterapkan.")
                elif method_balancing == "Random Undersampling":
                    X_train, y_train = RandomUnderSampler(random_state=random_state).fit_resample(X_train, y_train)
                    st.success("✅ Random Undersampling berhasil diterapkan.")
                else:
                    st.info("🚫 Anda memilih untuk tidak menggunakan balancing.")

                tampilkan_distribusi(y_train, "Distribusi Kelas Setelah Balancing")

                st.session_state.update({
                    "X_train": X_train,
                    "X_test": X_test,
                    "y_train": y_train,
                    "y_test": y_test,
                    "method_balancing": method_balancing
                })
                st.success("✅ Data berhasil di-split dan di-balance")
                st.write("DATA TRAINING =", X_train.shape)
                st.write("DATA TESTING =", X_test.shape)

    with tabs[2]:
        algoritma = st.selectbox("Pilih Algoritma", get_algoritma_list())
        tuning_method = st.selectbox("Metode Hyperparameter Tuning", ["None", "GridSearchCV", "RandomizedSearchCV"])
        cv_folds = st.slider("Jumlah Fold untuk Cross-Validation", 3, 10, 5)

        if st.button("🚀 Latih Model"):
            if "X_train" not in st.session_state:
                st.warning("❗ Silakan lakukan Split Data terlebih dahulu.")
            else:
                model, y_pred, y_proba = train_model(
                    st.session_state["X_train"], st.session_state["y_train"],
                    st.session_state["X_test"], st.session_state["y_test"],
                    algoritma=algoritma,
                    tuning_method=tuning_method,
                    cv_folds=cv_folds,
                    method_balancing=st.session_state.get("method_balancing", "None")
                )

                st.session_state.update({
                    'model': model,
                    'y_pred': y_pred,
                    'y_proba': y_proba
                })
                st.success("✅ Model berhasil dilatih")

    with tabs[3]:
        if check_session_keys(['model', 'X_test', 'y_test'], warning_message="❗ Data atau model belum lengkap."):
            acc, f1, cls_report, conf_matrix, roc_data, y_pred, labels = evaluate_model(
                st.session_state['model'],
                st.session_state['X_test'],
                st.session_state['y_test'],
                
            )

            st.session_state['y_pred'] = y_pred 

            st.subheader("📋 Classification Report")
            st.dataframe(cls_report)
            st.divider()
            st.metric("🎯 F1-Score", f"{f1:.4f}")
            st.metric("📏 Akurasi", f"{acc:.4f}")

            total = len(st.session_state['y_test'])
            benar = np.sum(st.session_state['y_test'] == st.session_state['y_pred'])
            salah = total - benar
            st.markdown(f"- Total data: **{total}**")
            st.markdown(f"- ✅ Prediksi benar: **{benar}**")
            st.markdown(f"- ❌ Prediksi salah: **{salah}**")
            st.divider()

            fig_cm = plot_confusion_matrix(conf_matrix, class_names=labels)
            st.pyplot(fig_cm)
            st.divider()

            if roc_data is not None:
                fpr, tpr, roc_auc = roc_data
                st.metric("📈 ROC-AUC", f"{roc_auc:.4f}")
                fig_roc = plot_roc_curve(fpr, tpr, roc_auc)
                st.pyplot(fig_roc)
            elif roc_data is None and len(np.unique(st.session_state['y_test'])) > 2:
                st.info("ℹ️ ROC Curve hanya untuk klasifikasi Single-Class.")
            else:
                st.info("📛 ROC Curve tidak tersedia untuk model ini.")

            st.divider()

            model_name = type(st.session_state['model']).__name__
            fpr_val, tpr_val, roc_auc_val = None, None, None
            if roc_data is not None:
                fpr_val, tpr_val, roc_auc_val = roc_data

            pdf_buffer = generate_evaluation_pdf(
                model_name=model_name,
                data_name="Data Evaluasi",
                total=total,
                benar=benar,
                salah=salah,
                acc=acc,
                report_dict=cls_report,
                conf_matrix=conf_matrix,
                y_true=st.session_state['y_test'],
                fpr=fpr_val,
                tpr=tpr_val,
                roc_auc=roc_auc_val
            )

            st.download_button(
                label="📥 Download Hasil Test (PDF)",
                data=pdf_buffer,
                file_name=f"hasil_Testing_{model_name}.pdf",
                mime="application/pdf"
            )

    with tabs[4]:
        nama_file = st.text_input("Masukkan nama file model (tanpa ekstensi)", value="model_saya")

        if not nama_file.strip():
            st.warning("❗ Nama file tidak boleh kosong.")
        else:
            st.session_state["nama_file"] = nama_file

        if st.button("📦 Download Model (.zip)", type="primary"):
            if "model" in st.session_state:
                fitur_model = st.session_state["X_train"].columns.tolist()
                sukses, hasil = zip_model(st.session_state["model"], fitur_model, nama_file)

                if sukses:
                    st.success("✅ Model berhasil dikemas ke dalam file ZIP.")
                    st.download_button(
                        label="⬇️ Unduh Model (.zip)",
                        data=hasil,
                        file_name=f"{nama_file}.zip",
                        mime="application/zip"
                    )
                else:
                    st.error(f"Gagal membuat file ZIP: {hasil}")
            else:
                st.warning("❗ Model belum dilatih atau dimuat.")

    if st.button("🔄 Reset Data", type="secondary"):
        st.session_state["model_key"] = f"model_uploader_{np.random.randint(1000)}"
        st.session_state["upload_key"] = f"uploader_{np.random.randint(1000)}"
        reset_data()

render_footer()
