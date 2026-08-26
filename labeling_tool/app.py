"""
FinText-QC Labeling Tool
Streamlit app untuk melabeli teks SMS/chat sesuai LABELING_GUIDELINE.md

Cara pakai:
    streamlit run labeling_tool/app.py -- --pass_name pass1
    streamlit run labeling_tool/app.py -- --pass_name pass2
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

LABELS = ["FRAUD_SCAM", "PROMO_LEGIT", "NORMAL", "OTHER_SPAM"]
INPUT_PATH = "data/processed/cleaned.jsonl"


def parse_pass_name() -> str:
    """Ambil nama pass (pass1/pass2) dari argumen CLI.
    Streamlit sudah membuang '--' pemisah sebelum meneruskan ke script,
    jadi sys.argv[1:] langsung berisi argumen milik script ini.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass_name", default="pass1")
    parsed, _ = parser.parse_known_args(sys.argv[1:])
    return parsed.pass_name


def load_records(path: str) -> list[dict]:
    if not os.path.exists(path):
        st.error(f"File input tidak ditemukan: {path}. Jalankan ingestion service dulu (Tahap 2).")
        st.stop()
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def load_existing_labels(output_path: str) -> dict:
    """Load label yang sudah pernah disimpan, supaya bisa lanjut kalau app ditutup."""
    if not os.path.exists(output_path):
        return {}
    existing = {}
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                existing[row["id"]] = row
    return existing


def save_label(output_path: str, record: dict, label: str, pass_name: str, notes: str = ""):
    entry = {
        "id": record["id"],
        "text": record["text"],
        "label": label,
        "pass_name": pass_name,
        "labeled_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Append-only log; kalau id sama muncul lagi, kita anggap update (ambil terakhir)
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def main():
    pass_name = parse_pass_name()
    output_path = f"data/labeled/{pass_name}.jsonl"

    st.set_page_config(page_title=f"FinText-QC Labeling — {pass_name}", layout="centered")
    st.title(f"📋 FinText-QC Labeling Tool")
    st.caption(f"Sesi: **{pass_name}** — ikuti LABELING_GUIDELINE.md")

    records = load_records(INPUT_PATH)
    existing_labels = load_existing_labels(output_path)

    # Cari record pertama yang belum dilabeli di sesi ini
    unlabeled = [r for r in records if r["id"] not in existing_labels]

    progress = len(existing_labels)
    total = len(records)
    st.progress(progress / total if total else 0)
    st.write(f"Progress: **{progress}/{total}** data sudah dilabeli di sesi ini")

    if not unlabeled:
        st.success("Semua data sudah dilabeli untuk sesi ini! 🎉")
        st.write("Lanjut ke Tahap 4 untuk analisis agreement antar pass.")
        return

    current = unlabeled[0]

    st.subheader("Teks yang perlu dilabeli:")
    st.info(current["text"])

    with st.expander("📖 Lihat ringkasan guideline"):
        st.markdown("""
        - **FRAUD_SCAM**: minta OTP/PIN, iming-iming hadiah + link, mengaku bank/e-wallet resmi minta data sensitif
        - **PROMO_LEGIT**: promosi resmi, tidak minta data sensitif
        - **NORMAL**: notifikasi transaksi wajar, obrolan personal
        - **OTHER SPAM**: Pesan yang bersifat spam/promosi tapi TIDAK terkait finansial
        """)

    col1, col2, col3, col4 = st.columns(4)
    chosen_label = None
    if col1.button("🚨 FRAUD_SCAM", use_container_width=True):
        chosen_label = "FRAUD_SCAM"
    if col2.button("📢 PROMO_LEGIT", use_container_width=True):
        chosen_label = "PROMO_LEGIT"
    if col3.button("✅ NORMAL", use_container_width=True):
        chosen_label = "NORMAL"
    if col4.button("🗑️ OTHER_SPAM", use_container_width=True):
        chosen_label = "OTHER_SPAM"

    notes = st.text_input("Catatan (opsional, misal kalau ini kasus ambigu):")

    if chosen_label:
        save_label(output_path, current, chosen_label, pass_name, notes)
        st.rerun()

    st.divider()
    if st.button("⏭️ Skip (tandai untuk review nanti)"):
        save_label(output_path, current, "SKIPPED", pass_name, notes)
        st.rerun()


if __name__ == "__main__":
    main()