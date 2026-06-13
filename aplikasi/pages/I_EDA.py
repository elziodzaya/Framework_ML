import streamlit as st
import pandas as pd
import numpy as np
from utils.footer import render_footer
from utils.session_utils import upload_data, reset_data
from sklearn.model_selection import train_test_split
import os
from io import BytesIO
from utils.ui_utils import render_centered_title
import base64
from utils.preprocessing import (
    get_info_dataframe, remove_duplicates, encode_columns, 
    remove_outliers, handle_missing_values,save_data,
    plot_boxplot, remove_columns, detect_outliers,
    plot_correlation_heatmap, plot_correlation_bar,get_correlation_bar_data
)
import warnings
warnings.filterwarnings("ignore")


    
render_centered_title("🔍 Exploratory Data Analysis (EDA)")
st.markdown("""
<div style="text-align: center;">
This page serves to explore and analyze data aimed at exploring, analyzing, and understanding data before conducting further analysis or modeling on the machine
 </div>
""", unsafe_allow_html=True)
st.divider()
# Upload file
if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = "uploader_1"

uploaded_file = st.file_uploader("📁 Upload Data CSV", type=["csv"], key=st.session_state["upload_key"])
upload_data(uploaded_file)

if "df" in st.session_state and st.session_state.df is not None:
    df = st.session_state.df.copy()
    st.subheader("📋  Data Updated Preview")
    st.dataframe(df.head())
    st.write(f"📐 DIMENSI DATA: {df.shape[0]} Baris × {df.shape[1]} Kolom")
else:
    st.info("Please upload the CSV file first.!")

if "df" in st.session_state and st.session_state.df is not None:
    df = st.session_state.df
    sidebar_option = st.sidebar.radio("📌 Select Menu", ["Data Information", "Data Cleaning", "Data Split", "Data Transformation"])

    if sidebar_option == "Data Information":
        st.subheader("🧾 DATA INFORMATION")
        tab1, tab2 = st.tabs(["🧠 Data Structure", "📊  Data Statistics"])

        with tab1:
            info_df = get_info_dataframe(df)
            st.table(info_df)

        with tab2:
            st.subheader("📑 Numerical Column Statistics")
            st.dataframe(df.describe().round(2))
            obj_cols = df.select_dtypes(include='object').columns.tolist()
            if obj_cols:
                stats_object = df[obj_cols].describe().transpose()
                st.subheader("📑 Categorical Column Statistics")
                stats_object['Kategori'] = stats_object.index.map(
                lambda col: ", ".join(map(str, df[col].unique()))[:100] + '...'
            )
                st.dataframe(stats_object)
            else:
                st.info("No categorical (object) columns available.")

    elif sidebar_option == "Data Cleaning":
        st.subheader("🧹 DATA CLEANING")
        tab3, tab4, tab5, tab6 = st.tabs(["🔁 Duplicate", "❓ Missing Value", "⚠️ Outlier", "🗑️ Delete Column"])

        with tab3:
            duplicated = df[df.duplicated()]
            st.write(f"Duplicate Data: {duplicated.shape[0]}")
            st.dataframe(duplicated)
            if st.button("🧹 Remove Duplicates"):
                st.session_state.df = remove_duplicates(df)
                st.success("Duplicate data successfully removed.")
                st.rerun()

        with tab4:
            missing = df.isnull().sum()
            st.write(missing[missing > 0])
            method_missing = st.radio("Handling Method", ["drop", "mean", "median"])
            if st.button("🔧 Tangani Missing Value"):
                st.session_state.df = handle_missing_values(df, method=method_missing)
                st.success(f"Missing values are handled with the method: {method_missing}.")
                st.rerun()

        with tab5:
            method_outlier = st.radio("Outlier Detection Method", ["iqr", "zscore"])
            label_col = st.selectbox("Select label/output column", df.columns)
            st.session_state.label_column = label_col

            outlier_mask, numeric_cols = detect_outliers(df, method=method_outlier, label_col=label_col)
            st.warning(f"Number of data detected as outliers: {outlier_mask.sum()}")

            if st.button("🧹 Remove Outliers"):
                st.session_state.df = remove_outliers(df, outlier_mask)
                st.success(f"Outliers successfully removed using the method: {method_outlier}.")
                st.rerun()

            st.subheader("📦 Boxplot Visualization")
            selected_col = st.selectbox("Select Column for Boxplot", [col for col in numeric_cols if col != label_col])
            if selected_col:
                fig = plot_boxplot(df, selected_col)
                st.pyplot(fig)

        with tab6:
            selected_cols_to_drop = st.multiselect("Select column to delete", df.columns.tolist())
            if st.button("🗑️ Delete Column"):
                if selected_cols_to_drop:
                    st.session_state.df = remove_columns(df, selected_cols_to_drop)
                    st.success(f"{len(selected_cols_to_drop)} Column successfully deleted.")
                    st.rerun()
                else:
                    st.warning("Select at least one column to delete.")
    elif sidebar_option == "Data Split":
        st.subheader("🔀 SPLIT DATA:  TRAIN & EVALUATION")

        test_size = st.slider("Evaluation Data Proportion (test)", min_value=0.1, max_value=0.5, value=0.2, step=0.05)
        random_state = st.number_input("Random State (opsional)", min_value=0, value=42)
        eval_filename = st.text_input("Evaluation data filename (without extension)", value="data_evaluasi")

        if st.button("🚀 Split Data"):
            train_df, eval_df = train_test_split(df, test_size=test_size, random_state=random_state)
            st.session_state.df = train_df

            eval_csv = eval_df.to_csv(index=False).encode('utf-8')
            eval_xlsx_io = BytesIO()
            eval_df.to_excel(eval_xlsx_io, index=False, engine='openpyxl')
            eval_xlsx_io.seek(0)

            st.success(f"✅ Data successfully split. Evaluation data has dimensions:{eval_df.shape[0]} baris × {eval_df.shape[1]} kolom.")

            st.download_button("⬇️ Download CSV Evaluasi", data=eval_csv, file_name=f"{eval_filename}.csv", mime="text/csv")
            st.download_button("⬇️ Download Excel Evaluasi", data=eval_xlsx_io, file_name=f"{eval_filename}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif sidebar_option == "Data Transformation":
        st.subheader("🧬 DATA TRANSFORMATION")
        tab7, tab8 = st.tabs(["🔤 Encoding", "📈 Correlation"])

        with tab7:
            st.header("🔤 Categorical Data Encoding")
            obj_cols = df.select_dtypes(include='object').columns.tolist()

            if not obj_cols:
                st.info("There are no categorical columns.")
            else:
                encoding_method = st.radio("Select Encoding Method", ["Label Encoding", "One-Hot Encoding", "Manual Label Encoding"])
                selected_encoding_cols = st.multiselect("Select Columns for Encoding", obj_cols)

                manual_mappings = {}
                if encoding_method == "Manual Label Encoding":
                    for col in selected_encoding_cols:
                        unique_vals = df[col].dropna().unique().tolist()
                        st.markdown(f"**Column For Mapping {col}**")
                        mapping = {}
                        for val in unique_vals:
                            encoded_val = st.number_input(f"{val} (kolom {col})", key=f"{col}_{val}", step=1)
                            mapping[val] = int(encoded_val)
                        manual_mappings[col] = mapping

                if st.button("🚀 Encoding"):
                    if selected_encoding_cols:
                        encoded_df, encoding_info = encode_columns(df, selected_encoding_cols, encoding_method, manual_mappings)
                        st.session_state.df = encoded_df
                        st.success("Features Encoding Success.")
                        st.rerun()
                    else:
                        st.warning("Minimum Select One Colums.")

            st.markdown("---")
            st.subheader("🎯 TARGET COLUMN ENCODING")
            target_col = st.selectbox("Select Target Column", df.columns)
            label_encoding_method = st.radio("Encoding Method ", ["Label Encoding", "Manual Label Encoding"], key="target_enc_method")

            manual_target_map = {}
            if label_encoding_method == "Manual Label Encoding":
                unique_vals = df[target_col].dropna().unique().tolist()
                st.write("Enter Manual Mapping:")
                for val in unique_vals:
                    encoded_val = st.number_input(f"{val}", step=1, key=f"label_{val}")
                    manual_target_map[val] = int(encoded_val)

            if st.button("🔐 Encode Target"):
                if target_col:
                    if label_encoding_method == "Manual Label Encoding":
                        df[target_col] = df[target_col].map(manual_target_map)
                        st.session_state.df = df
                        st.session_state.label_column = target_col
                        st.success("target/label successfully encoded")
                        st.rerun()
                    else:
                        encoded_df, label_map = encode_columns(df, [target_col], "Label Encoding")
                        st.session_state.df = encoded_df
                        st.session_state.label_column = target_col
                        st.session_state.label_mapping = label_map[target_col]
                        st.rerun()
                else:
                    st.warning("Select the target column first.")

        with tab8:
            st.header("📈 CORRELATION ANALYSIS")
            correlation_method = st.radio("Select Correlation Plot Type", ["Heatmap", "Bar Chart"])
            corr_matrix = df.select_dtypes(include=np.number).corr()

            if correlation_method == "Heatmap":
                fig = plot_correlation_heatmap(corr_matrix)
            else:
                target_col = st.selectbox("Select Correlation Target Column", corr_matrix.columns)
                target_corr = get_correlation_bar_data(df, target_col)
                fig = plot_correlation_bar(target_corr, target_col)


            st.pyplot(fig)
        st.markdown("---")

    st.subheader("📥 Download Data")
    custom_filename = st.text_input("Enter the file name (without extension):", value="databersih")


    if st.button("⬇️ Download Data", type="primary"):
        if custom_filename.strip() == "":
            st.warning("File name cannot be empty.")
        else:
            buffers = save_data(df, custom_filename)
            st.success("✅ Data successfully prepared for download.")

            st.download_button(
                label="⬇️ Download CSV",
                data=buffers["csv"][1],
                file_name=buffers["csv"][0],
                mime="text/csv"
            )

            st.download_button(
                label="⬇️ Download Excel",
                data=buffers["excel"][1],
                file_name=buffers["excel"][0],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    if st.button("🔄 Reset Data"):
        reset_data()
        st.rerun()

# Footer
render_footer()




