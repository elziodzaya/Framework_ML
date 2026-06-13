import numpy as np
import pandas as pd
import io
import zipfile
import json
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    confusion_matrix, roc_curve, auc
)
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from joblib import dump

# =======================
# 1. Model & Hyperparameter
# =======================

def get_algoritma_list():
    return [
        "Decision Tree", "Logistic Regression", "Ridge Classifier",
        "Random Forest", "Extra Trees", "AdaBoost", "Gradient Boosting",
        "XGBoost", "LightGBM", "CatBoost", "SVM", "K-Nearest Neighbors", "Naive Bayes"
    ]

def get_model_and_params(algoritma):
    model_options = {
        "Decision Tree": DecisionTreeClassifier(),
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Ridge Classifier": RidgeClassifier(),
        "Random Forest": RandomForestClassifier(),
        "Extra Trees": ExtraTreesClassifier(),
        "AdaBoost": AdaBoostClassifier(),
        "Gradient Boosting": GradientBoostingClassifier(),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
        "LightGBM": LGBMClassifier(),
        "CatBoost": CatBoostClassifier(verbose=0),
        "SVM": SVC(probability=True),
        "K-Nearest Neighbors": KNeighborsClassifier(),
        "Naive Bayes": GaussianNB()
    }

    param_grids = {
        "Decision Tree": {"max_depth": [3, 5, 10, None], "criterion": ["gini", "entropy"]},
        "Logistic Regression": {"C": [0.01, 0.1, 1, 10], "solver": ["lbfgs", "liblinear"]},
        "Ridge Classifier": {"alpha": [0.1, 1.0, 10.0]},
        "Random Forest": {"n_estimators": [100, 200], "max_depth": [5, 10, None]},
        "Extra Trees": {"n_estimators": [100, 200], "max_depth": [5, 10, None]},
        "AdaBoost": {"n_estimators": [50, 100], "learning_rate": [0.5, 1.0]},
        "Gradient Boosting": {"n_estimators": [100, 200], "learning_rate": [0.05, 0.1], "max_depth": [3, 5]},
        "XGBoost": {"n_estimators": [100, 200], "learning_rate": [0.05, 0.1], "max_depth": [3, 5]},
        "LightGBM": {"n_estimators": [100, 200], "learning_rate": [0.05, 0.1], "num_leaves": [31, 64]},
        "CatBoost": {"iterations": [100, 200], "learning_rate": [0.05, 0.1], "depth": [3, 5, 7]},
        "SVM": {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"]},
        "K-Nearest Neighbors": {"n_neighbors": [3, 5, 11], "weights": ["uniform", "distance"]},
        "Naive Bayes": {}
    }

    return model_options.get(algoritma), param_grids.get(algoritma, {})

# =======================
# 2. Training Model
# =======================

def train_model(X_train, y_train, X_test, y_test, algoritma, tuning_method="None", cv_folds=5, method_balancing="None"):
    model, param_grid = get_model_and_params(algoritma)

    if method_balancing == "class_weight" and hasattr(model, 'class_weight'):
        model.set_params(class_weight='balanced')

    if tuning_method == "GridSearchCV" and param_grid:
        model = GridSearchCV(model, param_grid, cv=cv_folds, n_jobs=1)
    elif tuning_method == "RandomizedSearchCV" and param_grid:
        model = RandomizedSearchCV(model, param_grid, n_iter=5, cv=cv_folds, n_jobs=-1, random_state=42)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") and len(np.unique(y_test)) == 2 else None

    return model, y_pred, y_proba

# =======================
# 3. Evaluasi Model
# =======================
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") and len(np.unique(y_test)) == 2 else None

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    
    labels = sorted(np.unique(y_test))
    conf_matrix = confusion_matrix(y_test, y_pred, labels=labels)

    roc_data = None
    if y_proba is not None:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        roc_data = (fpr, tpr, roc_auc)

    return acc, f1, report_dict, conf_matrix, roc_data, y_pred, labels

# =======================
# 4. Visualisasi
# =======================

def tampilkan_distribusi(y, title="Distribusi Kelas"):
    value_counts = y.value_counts()
    total = len(y)
    percentages = value_counts / total * 100

    fig, ax = plt.subplots(figsize=(5, 3))
    sns.countplot(x=y, hue=y, ax=ax, palette='Set2', legend=False)
    ax.set_title(title, fontsize=6)
    ax.set_xlabel("Kelas", fontsize=5)
    ax.set_ylabel("Jumlah", fontsize=5)

    for p in ax.patches:
        count = int(p.get_height())
        pct = count / total * 100
        label = f"{count} ({pct:.1f}%)"
        ax.annotate(label,
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha='center', va='bottom', fontsize=5, color='black')

    if ax.legend_:
        ax.legend_.remove()

    plt.tight_layout()
    st.pyplot(fig)

def plot_confusion_matrix(cm, class_names=None, title="Confusion Matrix"):
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=class_names, yticklabels=class_names, linewidths=0.5, linecolor='gray')
    ax.set_xlabel("Prediksi")
    ax.set_ylabel("Aktual")
    ax.set_title(title)
    plt.tight_layout()
    return fig

def plot_roc_curve(fpr, tpr, roc_auc):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(fpr, tpr, color='blue', label=f'AUC = {roc_auc:.2f}')
    ax.plot([0, 1], [0, 1], color='gray', linestyle='--')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve')
    ax.legend(loc='lower right')
    plt.tight_layout()
    return fig

# =======================
# 5. Save Model
# =======================

def zip_model(model, fitur_model, nama_file):
    import pickle
    try:
        joblib_buffer = io.BytesIO()
        dump(model, joblib_buffer)
        joblib_buffer.seek(0)

        pkl_buffer = io.BytesIO()
        pickle.dump(model, pkl_buffer)
        pkl_buffer.seek(0)

        fitur_json = json.dumps({"fitur": fitur_model}, indent=2)
        fitur_buffer = io.BytesIO(fitur_json.encode('utf-8'))

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(f"{nama_file}.joblib", joblib_buffer.getvalue())
            zip_file.writestr(f"{nama_file}.pkl", pkl_buffer.getvalue())
            zip_file.writestr(f"{nama_file}_fitur.json", fitur_buffer.getvalue())

        zip_buffer.seek(0)
        return True, zip_buffer
    except Exception as e:
        return False, str(e)

def plot_confusion_matrix_to_buffer(conf_matrix, labels):
    fig, ax = plt.subplots(figsize=(4, 3))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels, cbar=False, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf


