import pandas as pd
import streamlit as st


def predict_from_manual_input(model, features, cat_cols, num_cols, label_encoders, cat_values, target_encoder, metadata):
    with st.form("manual_input_form"):
        input_data = {}

        # Input untuk fitur kategorik
        for col in cat_cols:
            val = st.selectbox(f"{col}", cat_values[col])
            input_data[col] = label_encoders[col][val]

        # Input untuk fitur numerik dengan validasi min-max
        for col in num_cols:
            min_val = metadata.get(col, {}).get("min", 0.0)
            max_val = metadata.get(col, {}).get("max", 100000.0)
            val = st.number_input(
                f"{col} (Rentang: {min_val} - {max_val})",
                min_value=float(min_val),
                max_value=float(max_val),
                step=0.1,
                format="%.2f"
            )
            input_data[col] = val

        submitted = st.form_submit_button("Lakukan Prediksi")
        if submitted:
            input_df = pd.DataFrame([input_data])[features]
            prediction = model.predict(input_df)[0]  # prediction = 1, misalnya
            reverse_map = {v: k for k, v in target_encoder.items()}
            label_name = reverse_map.get(prediction, str(prediction))
            input_df["Prediksi"] = prediction  # tetap simpan angka (misalnya 1)

            return input_df, prediction, label_name  # ← kembalikan keduanya!


    return None, None, None

def predict_from_file_input(model, fitur_model, encoding_map, target_map):
    st.subheader("Unggah File CSV")
    file = st.file_uploader("Pilih file CSV", type=["csv"], key="csv_upload")
    if file is not None:
        df = pd.read_csv(file)

        # Validasi kolom
        if not set(fitur_model).issubset(df.columns):
            st.error("Kolom pada data tidak sesuai dengan fitur model.")
            return None, None

        # Encode kategorikal
        for col, mapping in encoding_map.items():
            df[col] = df[col].map(mapping)

        # Prediksi
        predictions = model.predict(df[fitur_model])

        # Mapping hasil ke label asli
        inverse_map = {v: k for k, v in target_map.items()}
        prediction_labels = [inverse_map.get(pred, pred) for pred in predictions]

       
        df["Prediksi"] = prediction_labels
        return df, prediction_labels
    

    return None, None
