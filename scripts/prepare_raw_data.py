"""
Gabungkan file .txt dari dataset bopbi (per folder kategori) + seed data
NORMAL/PROMO_LEGIT buatan sendiri menjadi satu raw_sms.csv untuk ingestion.
"""
import csv
import os

BOPBI_REPO_PATH = "/tmp/sms-dataset"

# Hanya ambil folder yang relevan konteks finansial + spam non-finansial
FOLDER_TO_HINT = {
    "loan": "fraud_candidate",       # pinjol ilegal -> kandidat FRAUD_SCAM
    "prize": "fraud_candidate",      # scam hadiah -> kandidat FRAUD_SCAM
    "premium-sms": "other_spam_candidate",
    "non-provider-promo": "other_spam_candidate",
    "evil-service": "other_spam_candidate",
}

SEED_CSV = "data/raw/normal_promo_seed.csv"
OUTPUT_CSV = "data/raw/raw_sms.csv"


def load_bopbi_texts():
    rows = []
    for folder, hint in FOLDER_TO_HINT.items():
        folder_path = os.path.join(BOPBI_REPO_PATH, folder)
        if not os.path.isdir(folder_path):
            print(f"Skip {folder}: tidak ditemukan di {folder_path}")
            continue
        for fname in os.listdir(folder_path):
            if not fname.endswith(".txt"):
                continue
            with open(os.path.join(folder_path, fname), encoding="utf-8", errors="ignore") as f:
                text = f.read().strip().replace("\n", " ").replace("\r", " ")
                if text:
                    rows.append({"text": text, "category_hint": hint})
    return rows


def load_seed_csv():
    rows = []
    with open(SEED_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def main():
    bopbi_rows = load_bopbi_texts()
    seed_rows = load_seed_csv()
    all_rows = bopbi_rows + seed_rows

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "category_hint"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Total data digabung: {len(all_rows)}")
    print(f"  - dari bopbi dataset: {len(bopbi_rows)}")
    print(f"  - dari seed manual  : {len(seed_rows)}")
    print(f"Tersimpan di: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()