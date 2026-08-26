"""
Tahap 4: Analisis Kualitas Data - Inter-Annotator Agreement
Membandingkan hasil pass1 vs pass2 untuk mengukur konsistensi labeling
dan mengidentifikasi kasus yang perlu revisi guideline.
"""
import json
import os

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

PASS1_PATH = "data/labeled/pass1.jsonl"
PASS2_PATH = "data/labeled/pass2.jsonl"
DISAGREEMENT_OUTPUT = "data/labeled/disagreements.jsonl"


def load_jsonl(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"File tidak ditemukan: {path}. Pastikan sudah menjalankan labeling untuk sesi ini."
        )
    records = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                # kalau id sama muncul lagi (relabel), ambil entry terakhir
                records[row["id"]] = row
    return records


def interpret_kappa(k: float) -> str:
    if k > 0.8:
        return "SANGAT BAIK (>0.8) - guideline sudah jelas dan konsisten diterapkan."
    elif k > 0.6:
        return "BAIK (0.6-0.8) - masih ada beberapa area ambigu, cek disagreement cases."
    elif k > 0.4:
        return "CUKUP (0.4-0.6) - guideline perlu direvisi di beberapa kategori."
    else:
        return "LEMAH (<0.4) - guideline kemungkinan ambigu atau kategori tumpang tindih."


def main():
    pass1 = load_jsonl(PASS1_PATH)
    pass2 = load_jsonl(PASS2_PATH)

    common_ids = sorted(set(pass1) & set(pass2))
    if not common_ids:
        print("Tidak ada id yang sama antara pass1 dan pass2. Pastikan kedua pass melabeli dataset yang sama.")
        return

    only_in_1 = set(pass1) - set(pass2)
    only_in_2 = set(pass2) - set(pass1)
    if only_in_1 or only_in_2:
        print(f"Peringatan: {len(only_in_1)} id hanya di pass1, {len(only_in_2)} hanya di pass2 (diabaikan dari analisis).")

    labels_1 = [pass1[i]["label"] for i in common_ids]
    labels_2 = [pass2[i]["label"] for i in common_ids]

    kappa = cohen_kappa_score(labels_1, labels_2)
    agreement_rate = sum(a == b for a, b in zip(labels_1, labels_2)) / len(common_ids)

    all_labels = sorted(set(labels_1) | set(labels_2))
    cm = confusion_matrix(labels_1, labels_2, labels=all_labels)

    print("=== Inter-Annotator Agreement Report ===")
    print(f"Total data dibandingkan : {len(common_ids)}")
    print(f"Agreement rate (raw)    : {agreement_rate:.2%}")
    print(f"Cohen's Kappa           : {kappa:.3f}")
    print(f"Interpretasi            : {interpret_kappa(kappa)}")
    print()
    print("Confusion Matrix (baris=pass1, kolom=pass2):")
    print(pd.DataFrame(cm, index=all_labels, columns=all_labels))

    # Simpan kasus disagreement -> bahan revisi guideline
    disagreements = [
        {
            "id": i,
            "text": pass1[i]["text"],
            "label_pass1": pass1[i]["label"],
            "label_pass2": pass2[i]["label"],
            "notes_pass1": pass1[i].get("notes", ""),
            "notes_pass2": pass2[i].get("notes", ""),
        }
        for i in common_ids
        if pass1[i]["label"] != pass2[i]["label"]
    ]

    os.makedirs(os.path.dirname(DISAGREEMENT_OUTPUT), exist_ok=True)
    with open(DISAGREEMENT_OUTPUT, "w", encoding="utf-8") as f:
        for d in disagreements:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"\n{len(disagreements)} kasus disagreement disimpan ke {DISAGREEMENT_OUTPUT}")
    print("Buka file ini untuk melihat pola kesalahan & jadi bahan revisi guideline (v1.2).")


if __name__ == "__main__":
    main()