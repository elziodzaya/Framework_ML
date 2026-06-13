# --- Import
import os, json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# =======================
# 1. INFO DATAFRAME
# =======================

def get_info_dataframe(df):
    """Mengembalikan info ringkas: jumlah null, tipe data, dan jumlah unik per kolom."""
    return pd.DataFrame({
        'Non-Null Count': df.notnull().sum(),
        'Data Type': df.dtypes.astype(str),
        'Unique Values': df.nunique()
    })

def get_statistik_numerik(df):
    return df.describe().round(2)

def get_statistik_kategorik(df):
    stats = df.describe(include='object').T
    stats['Daftar Kategori'] = stats.index.map(lambda col: ", ".join(map(str, df[col].unique()))[:100] + '...')
    return stats

# =======================
# 2. DUPLIKAT & MISSING
# =======================

def get_duplicates(df):
    return df[df.duplicated()]

def remove_duplicates(df):
    return df.drop_duplicates().reset_index(drop=True)

def get_missing_values(df):
    return df.isnull().sum()

def handle_missing_values(df, method='drop'):
    if method == 'drop':
        return df.dropna().reset_index(drop=True)
    elif method == 'mean':
        return df.fillna(df.mean(numeric_only=True)).reset_index(drop=True)
    elif method == 'median':
        return df.fillna(df.median(numeric_only=True)).reset_index(drop=True)
    else:
        raise ValueError("Gunakan metode 'drop', 'mean', atau 'median'.")

# =======================
# 3. OUTLIERS
# =======================

def detect_outliers(df, method='iqr', label_col=None):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if label_col in numeric_cols:
        numeric_cols.remove(label_col)

    outlier_mask = pd.Series(False, index=df.index)

    for col in numeric_cols:
        if method == 'iqr':
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            mask = (df[col] < lower) | (df[col] > upper)
        elif method == 'zscore':
            z_scores = (df[col] - df[col].mean()) / df[col].std()
            mask = z_scores.abs() > 3
        else:
            raise ValueError("Gunakan metode 'iqr' atau 'zscore'.")
        outlier_mask |= mask

    return outlier_mask, numeric_cols

def remove_outliers(df, outlier_mask):
    return df[~outlier_mask].reset_index(drop=True)

def handle_outliers(df, method='iqr', label_col=None):
    outlier_mask, _ = detect_outliers(df, method, label_col)
    return remove_outliers(df, outlier_mask)

def plot_boxplot(df, col):
    fig, ax = plt.subplots()
    sns.boxplot(x=df[col], ax=ax, color="skyblue")
    ax.set_title(f'Boxplot - {col}')
    return fig

# =======================
# 4. ENCODING
# =======================

from sklearn.preprocessing import LabelEncoder
def encode_columns(df, columns, method, manual_mappings=None):
    df_encoded = df.copy()
    encoding_info = {}

    for col in columns:
        if method == "Label Encoding":
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            encoding_info[col] = {label: int(i) for i, label in enumerate(le.classes_)}
        elif method == "One-Hot Encoding":
            df_encoded = pd.get_dummies(df_encoded, columns=[col])
            encoding_info[col] = "one-hot"
        elif method == "Manual Label Encoding":
            if manual_mappings and col in manual_mappings:
                df_encoded[col] = df_encoded[col].astype(str).map(manual_mappings[col])
                encoding_info[col] = manual_mappings[col]
            else:
                raise ValueError(f"Mapping manual kolom '{col}' tidak tersedia.")
    return df_encoded, encoding_info

# =======================
# 5. KORELASI
# =======================

def calculate_correlation(df):
    return df.select_dtypes(include=np.number).corr()

def plot_correlation_heatmap(df):
    corr = calculate_correlation(df)
    num_vars = len(corr.columns)
    plt.figure(figsize=(max(8, num_vars), max(6, num_vars)))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", square=True,
                cbar_kws={'shrink': 0.75}, linewidths=0.5, linecolor='gray')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return plt

def get_correlation_bar_data(df, target_col):
    corr = calculate_correlation(df)
    if target_col in corr.columns:
        return corr[target_col].drop(target_col).sort_values(ascending=False)
    else:
        raise ValueError("Kolom target tidak ditemukan dalam data korelasi.")

def plot_correlation_bar(target_corr, target_col):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=target_corr.values, y=target_corr.index, palette='viridis', ax=ax)
    ax.set_title(f"Korelasi terhadap {target_col}")
    ax.set_xlabel("Korelasi")
    ax.set_ylabel("Fitur")
    plt.tight_layout()
    return fig

# =======================
# 6. UTILITAS
# =======================

def remove_columns(df, columns_to_drop):
    return df.drop(columns=columns_to_drop)

from io import BytesIO

def save_data(df, filename="data"):
    """
    Mengembalikan file CSV dan Excel sebagai BytesIO (untuk download langsung oleh user).
    
    Parameters:
    - df: DataFrame
    - filename: nama file dasar (tanpa ekstensi)

    Returns:
    - Dictionary: {'csv': (filename, BytesIO), 'excel': (filename, BytesIO)}
    """
    # CSV
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)

    return {
        "csv": (f"{filename}.csv", csv_buffer),
        "excel": (f"{filename}.xlsx", excel_buffer)
    }
