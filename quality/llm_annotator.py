"""
Tahap 5: LLM-Assisted Labeling
Menjalankan model lewat Groq sebagai "annotator ketiga", membandingkan
hasilnya dengan label final manusia (ground truth), dan menganalisis
pola kesalahan LLM -- insight ini relevan untuk role yang menyiapkan
data training LLM.
"""
import json
import os
import time

from dotenv import load_dotenv
from groq import Groq
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
FINAL_LABELS_PATH = "data/labeled/final.jsonl"
LLM_OUTPUT_PATH = "data/labeled/llm_annotations.jsonl"
LABELS = ["FRAUD_SCAM", "PROMO_LEGIT", "NORMAL", "OTHER_SPAM"]

SYSTEM_PROMPT = f"""Kamu adalah annotator data yang mengklasifikasikan pesan SMS/chat
berbahasa Indonesia ke salah satu dari 4 kategori berikut:

- FRAUD_SCAM: indikasi penipuan finansial (phishing OTP/PIN, hadiah palsu,
  skema biaya tersembunyi/auto-subscribe, harga barang tidak wajar via
  kontak pribadi, mengaku bank/e-wallet resmi minta data sensitif,
  ATAU penawaran pinjaman online ilegal dengan pola: tanpa agunan, syarat
  hanya KTP/KK, bunga sangat rendah tidak wajar, proses instan, kontak
  hanya via WA/chat pribadi tanpa identitas resmi OJK)
- PROMO_LEGIT: promosi resmi yang mengajak tindakan ke depan, TIDAK minta
  data sensitif
- NORMAL: notifikasi transaksi yang sudah terjadi, atau obrolan personal wajar
- OTHER_SPAM: spam/iklan yang TIDAK terkait finansial (jasa umum, dll)

Balas HANYA dengan satu kata nama kategori di atas, tanpa penjelasan tambahan."""


def classify_text(client: Groq, text: str) -> tuple[str, str]:
    """Mengembalikan (label, raw_response) -- raw disimpan untuk debugging."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,
        max_tokens=500,          # ruang cukup untuk reasoning + jawaban akhir
        reasoning_effort="low",  # minimalkan reasoning, kita cuma butuh 1 kata
    )
    raw = (response.choices[0].message.content or "").strip().upper()
    for label in LABELS:
        if label in raw:
            return label, raw
    return "UNKNOWN", raw


def load_final_labels():
    records = []
    with open(FINAL_LABELS_PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def main():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY tidak ditemukan. Cek file .env kamu.")

    client = Groq(api_key=api_key)
    records = load_final_labels()

    results = []
    for i, r in enumerate(records, 1):
        try:
            llm_label, raw_response = classify_text(client, r["text"])
            if llm_label == "UNKNOWN":
                print(f"  [debug] raw response kosong/tidak dikenali: {raw_response!r}")
        except Exception as e:
            print(f"Error di id={r['id']}: {e}")
            llm_label = "ERROR"

        results.append({
            "id": r["id"],
            "text": r["text"],
            "human_label": r["final_label"],
            "llm_label": llm_label,
            "match": llm_label == r["final_label"],
        })
        print(f"[{i}/{len(records)}] {r['id']}: human={r['final_label']} | llm={llm_label}")
        time.sleep(0.3)  # jaga-jaga rate limit free tier

    os.makedirs(os.path.dirname(LLM_OUTPUT_PATH), exist_ok=True)
    with open(LLM_OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    valid_results = [r for r in results if r["llm_label"] not in ("ERROR", "UNKNOWN")]
    human_labels = [r["human_label"] for r in valid_results]
    llm_labels = [r["llm_label"] for r in valid_results]

    accuracy = sum(r["match"] for r in valid_results) / len(valid_results)

     # Simpan riwayat evaluasi supaya bisa lihat tren before/after guideline revision
    HISTORY_PATH = "data/labeled/llm_eval_history.jsonl"
    recall_fraud = sum(
        1 for r in valid_results if r["human_label"] == "FRAUD_SCAM" and r["match"]
    ) / max(1, sum(1 for r in valid_results if r["human_label"] == "FRAUD_SCAM"))

    history_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": MODEL_NAME,
        "guideline_version": os.getenv("GUIDELINE_VERSION", "unknown"),
        "accuracy": round(accuracy, 4),
        "recall_fraud_scam": round(recall_fraud, 4),
        "n_samples": len(valid_results),
    }
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(history_entry, ensure_ascii=False) + "\n")
    print(f"\nRun history dicatat ke {HISTORY_PATH}")

    print("\n=== LLM vs Human Labeling Report ===")
    print(f"Model             : {MODEL_NAME}")
    print(f"Total data        : {len(results)}")
    print(f"Berhasil diproses : {len(valid_results)}")
    print(f"Accuracy (vs human): {accuracy:.2%}")
    print()
    print(classification_report(human_labels, llm_labels, labels=LABELS, zero_division=0))
    print("Confusion Matrix (baris=human, kolom=llm):")
    print(pd.DataFrame(confusion_matrix(human_labels, llm_labels, labels=LABELS), index=LABELS, columns=LABELS))

    disagreements = [r for r in valid_results if not r["match"]]
    print(f"\n{len(disagreements)} kasus LLM berbeda dari label manusia. Contoh:")
    for d in disagreements[:5]:
        print(f"  - [{d['human_label']} vs {d['llm_label']}] {d['text'][:80]}...")


if __name__ == "__main__":
    main()