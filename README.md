# FinText-QC — Fraud/Scam Text Labeling & Data Quality Pipeline

An end-to-end simulation pipeline for collecting, validating, labeling, and
measuring the quality of Indonesian-language financial fraud text data —
designed to mirror the process of preparing LLM training data in a digital
payments context.

🔗 **[Live Dashboard Demo](https://fintext-qc.streamlit.app)**

---

## 1. Problem Statement

Most data science projects focus on model building, even though model
quality depends heavily on the quality of the data behind it — a process
that's rarely documented explicitly. This project addresses the question:

> **Can we build a data collection and labeling process for Indonesian
> financial fraud text that is consistent and measurably high-quality —
> approaching industry standards for LLM training data preparation?**

Specifically, three sub-questions this project answers:
1. How consistent is a single annotator when labeling the same data at different times? (→ inter-annotator agreement)
2. Can an LLM be relied upon as a "third annotator" for large-scale validation? (→ LLM-assisted evaluation)
3. How does a labeling guideline evolve when confronted with real-world data? (→ iterative guideline refinement)

## 2. Data Selection

The public [Indonesia SMS Spam Dataset](https://github.com/bopbi/indonesia-sms-spam-dataset)
was selected because it contains Indonesian-language SMS spam under the
`loan` and `prize` categories — the two patterns most relevant to financial
fraud (illegal online lending & prize scams).

**Limitation found & how it was addressed:** the source dataset turned out
to contain spam only, with no legitimate message examples at all. To address
this, `NORMAL`/`PROMO_LEGIT` seed data was created manually (not claimed to
be real user data) — this decision is documented explicitly rather than
hidden, since being transparent about data limitations is part of good data
quality practice.

## 3. Methodology

### Architecture

```
Raw SMS Data (public dataset + manual seed)
        │
        ▼
[Go] Ingestion Service — validation, dedup, cleaning
        │
        ▼
[Python/Streamlit] Manual Labeling Tool — dual-pass annotation
        │
        ▼
[Python] Quality Analysis — Cohen's Kappa, disagreement detection
        │
        ▼
[Groq LLM] AI-Assisted Labeling — cross-validation
        │
        ▼
[Python/Streamlit] Trust & Quality Dashboard
```

### Tech Stack

| Component | Tools |
|---|---|
| Data Ingestion & Validation | Go |
| Manual Labeling Tool | Python, Streamlit |
| Quality Metrics | Python, scikit-learn (Cohen's Kappa) |
| AI-Assisted Labeling | Groq API (openai/gpt-oss-20b) |
| Dashboard | Python, Streamlit, Pandas |

### Iterative Guideline Process

The guideline ([`guideline/LABELING_GUIDELINE.md`](guideline/LABELING_GUIDELINE.md))
defines 4 categories: `FRAUD_SCAM`, `PROMO_LEGIT`, `NORMAL`, `OTHER_SPAM`.
It was revised 3 times (v1.1 → v1.3) based on empirical findings from the
labeling and evaluation process — not designed once and left unchanged:

- **v1.1 → v1.2**: revised after Cohen's Kappa analysis (see section 4) revealed the FRAUD_SCAM definition was too narrow.
- **v1.2 → v1.3**: revised after LLM evaluation (see section 4) found that illegal online lending patterns weren't covered.

## 4. Findings & Conclusions

### Inter-Annotator Agreement

65 data points were labeled in 2 independent passes, compared using Cohen's Kappa:

| Metric | Value |
|---|---|
| Agreement rate (raw) | 95.38% |
| **Cohen's Kappa** | **0.901** (*almost perfect*, Landis & Koch scale) |
| Disagreement cases | 3 out of 65 |

### LLM-Assisted Labeling & Guideline Iteration

The `openai/gpt-oss-20b` model (via Groq) was used as a "third annotator" for
cross-validation against human labels:

| Guideline Version | Accuracy | FRAUD_SCAM Recall |
|---|---|---|
| v1.2 | 78.46% | 72.34% (34/47) |
| **v1.3** | **93.85%** | **93.62% (44/47)** |

**Root cause of the v1.2 → v1.3 gap:** the guideline did not explicitly
cover the **illegal online lending** pattern (40% of the dataset), causing
the model to misclassify it as OTHER_SPAM. After the revision, recall
improved significantly without reducing precision in other categories.

### Known Limitations

4 remaining disagreement cases (after v1.3) were deliberately **not**
patched further, to avoid overfitting the guideline to a small sample (n=65):
- The model shows **keyword bias**: messages mentioning "OTP" tend to be
  classified as FRAUD_SCAM even when the context is an official
  anti-phishing message.
- The model is less consistent at detecting fraud disguised as official
  promotions (real brand names, heavy leetspeak formatting).
- One case (a supernatural-style testimonial) sits in a gray area between
  FRAUD_SCAM and OTHER_SPAM even for human annotators.

**Conclusion:** labeling guideline quality has a direct, measurable impact
on the quality of the resulting data (a 15.4 percentage-point accuracy delta
from a single revision cycle), and LLM evaluation is an effective mechanism
for detecting guideline gaps that human annotators may not notice.

## 5. Report & Presentation

- **[Live Dashboard](https://fintext-qc.streamlit.app)** — a visual summary of all findings above (label distribution, accuracy trend per guideline revision, confusion matrix, known limitations).

![FinText-QC Trust Dashboard](assets/dashboard.png)

- Full history of design decisions & guideline revisions: [`guideline/LABELING_GUIDELINE.md`](guideline/LABELING_GUIDELINE.md)

---

## How to Run

```bash
# 1. Data ingestion & validation
cd ingestion && go run main.go -input=../data/raw/raw_sms.csv

# 2. Manual labeling (2 passes)
streamlit run labeling_tool/app.py -- --pass_name pass1
streamlit run labeling_tool/app.py -- --pass_name pass2

# 3. Final label resolution & agreement analysis
python quality/resolve_final_labels.py
python quality/agreement.py

# 4. LLM-assisted labeling (requires GROQ_API_KEY in .env)
python quality/llm_annotator.py

# 5. Dashboard
streamlit run dashboard/dashboard.py
```

## Project Structure

```
fintext-qc/
├── guideline/LABELING_GUIDELINE.md   # v1.0 -> v1.3, full revision history
├── ingestion/                        # Go: data validation & cleaning
├── labeling_tool/                    # Python: manual labeling tool
├── quality/                          # Python: metrics & LLM evaluation
├── dashboard/                        # Python: trust/quality dashboard
└── data/                             # raw, processed, labeled
```

## Notes

The original dataset is sourced from a public CC0 (free to use) repository.
NORMAL/PROMO_LEGIT seed data was created manually for demonstration purposes
and is not real transaction data from any user.

---

## Certificate & Badges

**Steven Oktavian**

<a href="https://www.credly.com/badges/a984c9e8-b817-4ac7-8af0-4a810aa0517b/public_url">
  <img src="https://images.credly.com/images/b38a42e0-dc58-4ce2-b6c0-28d978e8aaad/linkedin_thumb_image.png" width="350">
</a>
<a href="https://www.credly.com/badges/b434036f-9725-42bd-8fb6-fda18471fd78/public_url">
  <img src="https://images.credly.com/images/3f802526-7274-4230-91ab-f6d1a35340e6/linkedin_thumb_image.png" width="350">
</a>

*Introduction to Data Science & Python Essentials 2 — Cisco Networking Academy*