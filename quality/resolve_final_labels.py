"""
Tahap 5.1: Resolusi label final dari pass1, dengan override manual untuk
3 kasus disagreement yang sudah dianalisis & diputuskan sesuai guideline v1.2.
Ini jadi ground truth untuk evaluasi LLM-assisted labeling.
"""
import json

PASS1_PATH = "data/labeled/pass1.jsonl"
FINAL_OUTPUT_PATH = "data/labeled/final.jsonl"

# Keputusan final berdasarkan analisis Cohen's Kappa (lihat guideline v1.2,
# bagian "Catatan Revisi"). Didokumentasikan eksplisit di sini supaya jelas
# alasan tiap override, bukan cuma "ambil salah satu pass begitu saja".
MANUAL_OVERRIDES = {
    "sms-dataset-v1-000047": ("FRAUD_SCAM", "Hidden-fee auto-subscribe trap (RBT) -> masuk definisi FRAUD_SCAM v1.2"),
    "sms-dataset-v1-000049": ("FRAUD_SCAM", "Harga tidak wajar + transaksi via kontak pribadi -> pola scam jual-beli v1.2"),
    "sms-dataset-v1-000061": ("PROMO_LEGIT", "Ajakan tindakan ke depan ('cek aplikasi') -> heuristik tense PROMO_LEGIT v1.2"),
}


def main():
    resolved = []
    override_count = 0

    with open(PASS1_PATH, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            row_id = row["id"]

            if row_id in MANUAL_OVERRIDES:
                final_label, reason = MANUAL_OVERRIDES[row_id]
                override_count += 1
            else:
                final_label, reason = row["label"], "unchanged (pass1, no disagreement)"

            resolved.append({
                "id": row_id,
                "text": row["text"],
                "final_label": final_label,
                "resolution_reason": reason,
            })

    with open(FINAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        for r in resolved:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Total data final: {len(resolved)}")
    print(f"Override diterapkan: {override_count}")
    print(f"Tersimpan di: {FINAL_OUTPUT_PATH}")


if __name__ == "__main__":
    main()