"""
Tahap 6: Trust/Quality Dashboard
Merangkum seluruh proses data quality FinText-QC: distribusi label,
inter-annotator agreement, tren LLM evaluation, dan known limitations.
"""
import json
import os

import pandas as pd
import streamlit as st
from sklearn.metrics import cohen_kappa_score

FINAL_LABELS_PATH = "data/labeled/final.jsonl"
PASS1_PATH = "data/labeled/pass1.jsonl"
PASS2_PATH = "data/labeled/pass2.jsonl"
LLM_ANNOTATIONS_PATH = "data/labeled/llm_annotations.jsonl"
HISTORY_PATH = "data/labeled/llm_eval_history.jsonl"

st.set_page_config(page_title="FinText-QC Trust Dashboard", layout="wide")


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def compute_kappa():
    p1 = {r["id"]: r["label"] for r in load_jsonl(PASS1_PATH)}
    p2 = {r["id"]: r["label"] for r in load_jsonl(PASS2_PATH)}
    common = sorted(set(p1) & set(p2))
    if not common:
        return None
    return cohen_kappa_score([p1[i] for i in common], [p2[i] for i in common])


st.title("🛡️ FinText-QC Trust & Quality Dashboard")
st.caption("Ringkasan kualitas data pipeline: labeling consistency, LLM evaluation, known limitations")

# --- Row 1: Metrik utama ---
final_records = load_jsonl(FINAL_LABELS_PATH)
kappa = compute_kappa()
history = load_jsonl(HISTORY_PATH)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Data Berlabel", len(final_records))
col2.metric("Cohen's Kappa (pass1 vs pass2)", f"{kappa:.3f}" if kappa is not None else "N/A")

if history:
    latest = history[-1]
    first = history[0]
    delta_acc = latest["accuracy"] - first["accuracy"]
    col3.metric(
        f"LLM Accuracy ({latest['guideline_version']})",
        f"{latest['accuracy']:.1%}",
        delta=f"{delta_acc:+.1%} vs {first['guideline_version']}",
    )
    delta_recall = latest["recall_fraud_scam"] - first["recall_fraud_scam"]
    col4.metric(
        "Recall FRAUD_SCAM",
        f"{latest['recall_fraud_scam']:.1%}",
        delta=f"{delta_recall:+.1%}",
    )
else:
    col3.metric("LLM Accuracy", "Belum ada data")
    col4.metric("Recall FRAUD_SCAM", "Belum ada data")

st.divider()

# --- Row 2: Distribusi label & tren evaluasi ---
left, right = st.columns(2)

with left:
    st.subheader("📊 Distribusi Label (Final)")
    if final_records:
        df_final = pd.DataFrame(final_records)
        label_counts = df_final["final_label"].value_counts()
        st.bar_chart(label_counts)
    else:
        st.info("Belum ada data final. Jalankan Tahap 5.1 dulu.")

with right:
    st.subheader("📈 Tren LLM Accuracy per Revisi Guideline")
    if history:
        df_hist = pd.DataFrame(history)
        chart_data = df_hist.set_index("guideline_version")[["accuracy", "recall_fraud_scam"]]
        st.line_chart(chart_data)
        st.caption("Sumbu Y: proporsi (0-1). Naik = guideline makin jelas bagi LLM.")
    else:
        st.info("Belum ada riwayat evaluasi LLM.")

st.divider()

# --- Row 3: Confusion matrix terbaru ---
st.subheader("🔍 Confusion Matrix — LLM vs Human (Evaluasi Terakhir)")
llm_records = load_jsonl(LLM_ANNOTATIONS_PATH)
if llm_records:
    df_llm = pd.DataFrame(llm_records)
    valid = df_llm[~df_llm["llm_label"].isin(["ERROR", "UNKNOWN"])]
    labels = ["FRAUD_SCAM", "PROMO_LEGIT", "NORMAL", "OTHER_SPAM"]
    cm = pd.crosstab(valid["human_label"], valid["llm_label"]).reindex(
        index=labels, columns=labels, fill_value=0
    )
    st.dataframe(cm, width="stretch")

    with st.expander(f"🔎 Lihat {len(valid) - valid['match'].sum()} kasus disagreement"):
        for _, row in valid[~valid["match"]].iterrows():
            st.write(f"**[{row['human_label']} → {row['llm_label']}]** {row['text'][:150]}")
else:
    st.info("Belum ada hasil evaluasi LLM. Jalankan Tahap 5 dulu.")

st.divider()

# --- Row 4: Known Limitations ---
st.subheader("⚠️ Known Limitations")
st.markdown("""
- Model rentan **keyword bias**: pesan yang menyebut "OTP" cenderung diklasifikasikan
  FRAUD_SCAM meski konteksnya pesan resmi anti-phishing.
- Model kurang konsisten mendeteksi fraud yang dibungkus format promosi resmi
  (nama brand asli, format huruf kapital/leetspeak berat).
- Kasus testimoni gaya supranatural berada di area abu-abu bahkan untuk anotator manusia.
- Guideline sengaja tidak direvisi lebih lanjut untuk 4 kasus sisa, guna menghindari
  overfitting ke sample kecil (n=65).
""")