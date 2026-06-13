from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from fpdf import FPDF
from PIL import Image
import tempfile

def generate_evaluation_pdf(
    model_name,
    data_name,
    total,
    benar,
    salah,
    acc,
    report_dict,
    conf_matrix,
    y_true,
    fpr=None,
    tpr=None,
    roc_auc=None
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)

    # Judul
    # pdf.cell(0, 10, f"📄 Hasil Evaluasi Model: {model_name}", ln=True)
    pdf.cell(0, 10, f"[Report] Hasil Evaluasi Model: {model_name}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Dataset: {data_name}", ln=True)
    pdf.cell(0, 10, f"Total Data: {total}", ln=True)
    pdf.cell(0, 10, f"Prediksi Benar: {benar}", ln=True)
    pdf.cell(0, 10, f"Prediksi Salah: {salah}", ln=True)
    pdf.cell(0, 10, f"Akurasi: {acc:.4f}", ln=True)
    pdf.ln(5)

    # Classification Report
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Classification Report:", ln=True)
    pdf.set_font("Courier", '', 10)

    for label, metrics in report_dict.items():
        if isinstance(metrics, dict):
            line = f"{label}: " + ", ".join(f"{k}={v:.2f}" for k, v in metrics.items())
        else:
            continue
        pdf.multi_cell(0, 5, line)
    pdf.ln(5)

    # Confusion Matrix plot
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Confusion Matrix:", ln=True)

    fig_cm = plt.figure(figsize=(4, 3))
    import seaborn as sns
    labels = sorted(y_true.unique()) if hasattr(y_true, "unique") else sorted(np.unique(y_true))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels, yticklabels=labels, cbar=False)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()

    buf_cm = BytesIO()
    fig_cm.savefig(buf_cm, format='png', dpi=150)
    buf_cm.seek(0)
    plt.close(fig_cm)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
        tmp_img.write(buf_cm.read())
        tmp_img_path = tmp_img.name
        pdf.image(tmp_img_path, x=30, w=150)
    pdf.ln(5)

    # ROC Curve
    if fpr is not None and tpr is not None and roc_auc is not None:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "ROC Curve:", ln=True)

        fig_roc = plt.figure(figsize=(4, 3))
        plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.2f}")
        plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("ROC Curve")
        plt.legend()
        plt.tight_layout()

        buf_roc = BytesIO()
        fig_roc.savefig(buf_roc, format='png', dpi=150)
        buf_roc.seek(0)
        plt.close(fig_roc)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img_roc:
            tmp_img_roc.write(buf_roc.read())
            tmp_img_path_roc = tmp_img_roc.name
            pdf.image(tmp_img_path_roc, x=30, w=150)

    # Simpan ke buffer
    pdf_output = pdf.output(dest='S').encode('latin1')  # 'S' returns as string
    pdf_buffer = BytesIO(pdf_output)
    pdf_buffer.seek(0)
    return pdf_buffer

