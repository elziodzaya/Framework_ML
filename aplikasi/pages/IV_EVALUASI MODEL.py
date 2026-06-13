import streamlit as st
import pandas as pd
import numpy as np
import joblib
from utils.footer import render_footer
from utils.session_utils import upload_data, reset_data
from utils.ui_utils import render_centered_title
from utils.evaluation import generate_evaluation_pdf
from utils.model_utils import evaluate_model, plot_confusion_matrix, plot_roc_curve



render_centered_title("🧪 EVALUASI MODEL")
st.markdown("""
<div style="text-align: center;">
Halaman ini untuk mengevaluasi kinerja model ML terhadap data baru.
</div>
""", unsafe_allow_html=True)
st.divider()

# ========== Upload Model ==========
if "model_key" not in st.session_state:
    st.session_state["model_key"] = "model_uploader_1"

uploaded_model = st.file_uploader("📦 Upload File Model (.joblib)", type=["joblib"], key=st.session_state["model_key"])

if uploaded_model:
    try:
        model = joblib.load(uploaded_model)
        st.success("✅ Model berhasil dimuat!")
    except Exception as e:
        st.error(f"Gagal memuat model: {e}")
        st.stop()

    # ========== Upload Data ==========
    if "upload_key" not in st.session_state:
        st.session_state["upload_key"] = "uploader_1"
    uploaded_file = st.file_uploader("📄 Upload Data CSV", type=["csv"], key=st.session_state["upload_key"])
    upload_data(uploaded_file)

    if "df" in st.session_state and st.session_state.df is not None:
        df_eval = st.session_state.df.copy()
        st.success("✅ Data berhasil dimuat!")
        st.write("📋 Preview Data", df_eval.head())

        # ========== Pilih Kolom Target & Fitur ==========
        all_columns = df_eval.columns.tolist()
        target_column = st.selectbox("🎯 Pilih Kolom Target", options=all_columns)

        if target_column:
            feature_columns = [col for col in all_columns if col != target_column]
            selected_features = st.multiselect("🧩 Pilih Fitur", options=feature_columns, default=feature_columns)

            if st.button("🔍 Evaluasi Model"):
                try:
                    X_new = df_eval[selected_features]
                    y_true = df_eval[target_column]

                    # ✅ Evaluasi dengan utilitas utama
                    acc, f1, report_dict, conf_matrix, roc_data, y_pred, labels = evaluate_model(model, X_new, y_true)
                    fpr, tpr, roc_auc = roc_data if roc_data else (None, None, None)

                    # ========== METRIK ==========
                    total = len(y_true)
                    benar = np.sum(y_true == y_pred)
                    salah = total - benar

                    st.metric("📏 Akurasi", f"{acc:.4f}")
                    st.metric("🎯 F1-Score", f"{f1:.4f}")
                    st.markdown(f"- Total data: **{total}**")
                    st.markdown(f"- ✅ Prediksi benar: **{benar}**")
                    st.markdown(f"- ❌ Prediksi salah: **{salah}**")

                    st.subheader("📊 Classification Report")
                    st.dataframe(pd.DataFrame(report_dict).transpose())

                    # ========== CONFUSION MATRIX ==========
                    st.subheader("📉 Confusion Matrix")
                    fig_cm = plot_confusion_matrix(conf_matrix, class_names=labels)
                    st.pyplot(fig_cm)

                    # ========== ROC CURVE (Jika biner) ==========
                    if roc_data is not None:
                        st.subheader("📈 ROC Curve")
                        fig_roc = plot_roc_curve(fpr, tpr, roc_auc)
                        st.pyplot(fig_roc)
                        st.metric("📊 ROC-AUC", f"{roc_auc:.4f}")
                    else:
                        st.info("ℹ️ ROC Curve hanya untuk klasifikasi Single-Class.")

                    # ========== PDF DOWNLOAD ==========
                    pdf_file = generate_evaluation_pdf(
                        model_name=uploaded_model.name,
                        data_name=uploaded_file.name,
                        total=total,
                        benar=benar,
                        salah=salah,
                        acc=acc,
                        report_dict=report_dict,
                        conf_matrix=conf_matrix,
                        y_true=y_true,
                        fpr=fpr,
                        tpr=tpr,
                        roc_auc=roc_auc
                    )

                    st.download_button(
                        label="💾 Simpan Hasil Evaluasi ke PDF",
                        data=pdf_file,
                        file_name="hasil_evaluasi_model.pdf",
                        mime="application/pdf"
                    )

                except Exception as e:
                    st.error(f"❌ Gagal melakukan evaluasi: {e}")

        if st.button("🔄 Reset Data", type="secondary"):
            st.session_state["model_key"] = f"model_uploader_{np.random.randint(1000)}"
            st.session_state["upload_key"] = f"uploader_{np.random.randint(1000)}"
            reset_data()

render_footer()
