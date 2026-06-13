import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from utils.footer import render_footer
from utils.ui_utils import render_centered_title
from utils.session_utils import upload_model, upload_data, reset_data
from utils.aplikasi_utils import (
    save_manual_prediction_to_session,
    prepare_data_for_prediction,
    generate_result,
    process_manual_input,
    get_input_range,
    download_manual_history_csv,
    download_manual_history_excel
)



render_centered_title("🎯 APPLICATION")
st.markdown("""
<div style="text-align: center;">
        This page is an example implementation of a machine learning model that has been integrated into an application.
</div>
""",unsafe_allow_html=True)
st.divider()
# Upload model
model_upload = st.file_uploader("📁 Upload Model (.joblib)", type=["joblib"], key="model_upload_key")
if model_upload:
    upload_model(model_upload, session_key="trained_model", fitur_key="model_features")

model = st.session_state.get("trained_model")
fitur_model = st.session_state.get("model_features", [])

if model:
    st.divider()
    st.subheader("📂 Upload Data Mapping Label")

    label_upload = st.file_uploader("Upload labelled data (optional)", type=["csv", "xlsx"], key="data_label")
    if label_upload:
        upload_data(label_upload, session_key="label_data")

    data_input = st.session_state.get("label_data")
    target_col = None
    cat_cols = []
    numerik_cols = []
    cat_values = {}
    label_encoders = {}

    if data_input is not None:
        st.write("📊 Labels Data:")
        st.dataframe(data_input.head())

        target_col = st.selectbox("🎯 Select the Target/Label column", options=data_input.columns)

        if not fitur_model:
            fitur_model = [col for col in data_input.columns if col != target_col]

        for column in fitur_model:
            if data_input[column].dtype == 'object':
                cat_cols.append(column)
                cat_values[column] = list(data_input[column].unique())
                label_encoders[column] = {val: idx for idx, val in enumerate(data_input[column].unique())}
            else:
                numerik_cols.append(column)

    st.divider()
    st.subheader("🔢 Input Data Method ")
    tab1, tab2 = st.tabs(["📤 Upload File", "✍️ Manual Input "])

    with tab1:
        pred_data_upload = st.file_uploader("Upload File Data To Prediction", type=["csv", "xlsx"], key="prediksi_csv")
        if pred_data_upload and "predict_data" not in st.session_state:
            upload_data(pred_data_upload, session_key="predict_data")

        df_pred = st.session_state.get("predict_data")

        if df_pred is not None:
            st.write("📦 Data for Prediction:")
            st.dataframe(df_pred.head())

            if st.button("🚀 Prediction"):
                try:
                    df_input = prepare_data_for_prediction(df_pred.copy(), fitur_model, cat_cols, label_encoders)
                    hasil_df = generate_result(df_input, model, target_col=target_col, data_input=data_input)

                    st.success("✅ Prediction Result:")
                    st.dataframe(hasil_df)

                    st.subheader("📈 Visualisasi Hasil Prediksi")
                    fig, ax = plt.subplots()
                    hasil_df["Keterangan"].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
                    ax.set_ylabel('')
                    st.pyplot(fig)

                    csv_out = hasil_df.to_csv(index=False).encode('utf-8')
                    st.download_button("⬇️ Download Results  CSV", data=csv_out, file_name="hasil_prediksi.csv", mime="text/csv")
                except Exception as e:
                    st.error(f"An error occurred while processing the prediction: {e}")

    with tab2:
        st.markdown("### 📝 Manual Input Form")

        if "manual_history" not in st.session_state:
            st.session_state.manual_history = []

        if "manual_inputs" not in st.session_state:
            st.session_state.manual_inputs = {}

        with st.form("form_manual"):
            input_data = {}
            for fitur in fitur_model:
                key_name = f"input_{fitur}"

                if fitur in cat_cols and fitur in cat_values:
                    val = st.selectbox(
                        f"Enter value for **{fitur}**",
                        options=cat_values[fitur],
                        index=0,
                        key=key_name
                    )
                    input_data[fitur] = val
                elif fitur in numerik_cols:
                    min_val, max_val = get_input_range(data_input, fitur, target_col)
                    if min_val == max_val:
                        max_val = min_val + 1
                    default_val = float(st.session_state.manual_inputs.get(key_name, min_val))
                    safe_val = max(min_val, min(default_val, max_val))
                    val = st.number_input(
                        f"Enter value for **{fitur}**",
                        min_value=min_val,
                        max_value=max_val,
                        value=safe_val,
                        step=1.0,
                        key=key_name
                    )
                    input_data[fitur] = val
                    st.caption(f"Input Value Range: {min_val} – {max_val}")
                else:
                    val = st.text_input(f"Enter value for **{fitur}**", value="", key=key_name)
                    input_data[fitur] = val

            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button("🚀 Prediction")
            with col2:
                bersihkan = st.form_submit_button("🧹 Clear Form")

        if submitted:
            try:
                input_df = process_manual_input(input_data, fitur_model, cat_cols, label_encoders)
                pred = model.predict(input_df)[0]
                keterangan = dict(enumerate(data_input[target_col].unique())).get(pred, pred) if target_col else pred
                st.success(f"📌 Hasil Prediksi: **{pred}** - {keterangan}")

                save_manual_prediction_to_session(input_data, pred, keterangan)

                for fitur in fitur_model:
                    st.session_state.manual_inputs[f"input_{fitur}"] = input_data[fitur]
            except Exception as e:
                st.error(f"Gagal melakukan prediksi: {e}")

        if bersihkan:
            for fitur in fitur_model:
                key_name = f"input_{fitur}"
                if key_name in st.session_state:
                    del st.session_state[key_name]
                if key_name in st.session_state.manual_inputs:
                    del st.session_state.manual_inputs[key_name]
            st.rerun()

        if st.session_state.manual_history:
            st.subheader("📋 Manual Prediction History")
            df_history = pd.DataFrame(st.session_state.manual_history)
            st.dataframe(df_history)

            col1, col2 = st.columns([1, 1])
            with col1:
                csv_data = download_manual_history_csv()
                st.download_button("⬇️ Download CSV", data=csv_data, file_name="riwayat_manual.csv", mime="text/csv")
            with col2:
                excel_data = download_manual_history_excel()
                st.download_button("⬇️ Download Excel", data=excel_data, file_name="riwayat_manual.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("📭 No manual prediction history yet.")

    st.divider()
    if st.button("🔄 Reset Data", type="secondary"):
        reset_data()
        st.rerun()

render_footer()
