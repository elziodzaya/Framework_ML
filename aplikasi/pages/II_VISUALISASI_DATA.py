import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from utils.footer import  render_footer
from utils.session_utils import upload_data, reset_data
from utils.ui_utils import render_centered_title
import warnings
warnings.filterwarnings("ignore")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Silakan login terlebih dahulu melalui halaman Login.")
    st.stop()
# Judul Aplikasi
render_centered_title("📊 DATA VISUALIZATION ")
st.markdown("""
<div style="text-align: center;">Halaman ini berfungsi untuk melakukan representasi visual dari data asli (visualisasi Data),
yang dapat membantu kita melihat pola, tren, distribusi, hubungan antar variabel, dan insight penting.
</div>
""", unsafe_allow_html=True)
st.divider()
# Upload file
if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = "uploader_1"

uploaded_file = st.file_uploader("Unggah Data CSV", type=["csv","xlsx"], key=st.session_state["upload_key"])

upload_data(uploaded_file)
if "df" in st.session_state and st.session_state.df is not None:
    df = st.session_state.df.copy()
    st.subheader("📋 Preview Data Terkini")
    st.dataframe(df.head())
    st.write(f"DIMENSI DATA: {df.shape[0]} Baris × {df.shape[1]} Kolom")
    # Pilihan Grafik
    st.sidebar.header("📌 Pengaturan Grafik")
    chart_type = st.sidebar.selectbox("Pilih Jenis Chart", ["Countplot", "Pie Chart", "Histplot"])

    if chart_type == "Countplot":
        st.subheader("📊 Countplot")
        categorical_cols = df.select_dtypes(include=["object", "category", "int64"]).columns.tolist()
        col_x = st.sidebar.selectbox("Kolom Kategorikal (X)", categorical_cols)
        label_col = st.sidebar.selectbox("Label (Hue)", [None] + categorical_cols)

        fig, ax = plt.subplots(figsize=(10, 5))
        if label_col:
            ax = sns.countplot(data=df, x=col_x, hue=label_col, palette="Set2")
        else:
            ax = sns.countplot(data=df, x=col_x, palette="Set2")

        for container in ax.containers:
            ax.bar_label(container, fmt="%d", fontsize=8, padding=3)

        ax.set_xlabel(col_x, fontsize=12)
        ax.set_ylabel("Jumlah", fontsize=12)
        ax.set_title(f"Distribusi Countplot: {col_x}", fontsize=14)
        plt.xticks(rotation=45)
        plt.grid()
        st.pyplot(fig)

    elif chart_type == "Pie Chart":
        st.subheader("🥧 Pie Chart")
        categorical_cols = df.select_dtypes(include=["object", "category", "int64"]).columns.tolist()
        selected_col = st.sidebar.selectbox("Kolom Kategorikal", categorical_cols)

        pie_counts = df[selected_col].value_counts()

        fig, ax = plt.subplots(figsize=(6, 6))

        def func(pct, allvalues):
            absolute = int(np.round(pct / 100. * sum(allvalues)))
            return f"{absolute}\n({pct:.1f}%)"

        ax = pie_counts.plot.pie(autopct=lambda pct: func(pct, pie_counts), 
                                 labels=pie_counts.index,
                                 fontsize=8)

        ax.set_ylabel(selected_col, fontsize=12)
        ax.set_title(f"% Distribusi {selected_col}", fontsize=12)
        st.pyplot(fig)

    elif chart_type == "Histplot":
        st.subheader("📉 Histplot (Distribusi Data Numerik)")
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

        if not numeric_cols:
            st.warning("Tidak ada kolom numerik tersedia untuk Histplot.")
        else:
            selected_col = st.sidebar.selectbox("Pilih Kolom Numerik", numeric_cols)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(data=df, x=selected_col, bins=15, kde=True, color='skyblue', stat='percent', ax=ax)

            ax.set_xlabel(selected_col, fontsize=12)
            ax.set_ylabel("Persentase", fontsize=12)
            ax.set_title(f"Distribusi dari {selected_col}", fontsize=14)
            ax.yaxis.set_major_formatter(mtick.PercentFormatter())
            plt.grid()

            counts, bins = np.histogram(df[selected_col], bins=15)
            bin_centers = 0.5 * (bins[1:] + bins[:-1])
            for count, center in zip(counts, bin_centers):
                ax.text(center, count / len(df) * 100, f'{count}', ha='center', fontsize=9)

            st.pyplot(fig)

else:
    st.info("Silakan upload Data CSV atau Excel terlebih dahulu.!")
# Tombol Reset Data
# Tombol Reset Data
if "df" in st.session_state and st.session_state.df is not None:
    if st.button("🔄 Reset Data", type="secondary"):
        reset_data()
        st.rerun()  # Opsional: untuk menyegarkan halaman
render_footer()




