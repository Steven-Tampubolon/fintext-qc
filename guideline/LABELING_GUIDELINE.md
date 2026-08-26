# FinText-QC Labeling Guideline v1.3

## Purpose
Classify Indonesian-language SMS/chat messages into categories related to
financial fraud risk, simulating a trust & safety use case for a digital
payments platform.

## Label Categories

### 1. FRAUD_SCAM
Messages containing indications of financial fraud: transfer requests with
prize/lottery framing, phishing (requesting OTP/PIN/verification codes),
impersonating an official bank/e-wallet while requesting sensitive data,
suspicious links with money-related bait, **hidden-fee/auto-subscribe
schemes disguised as free offers (ringback tones, premium content, etc.),
or offers of high-value goods at unreasonably low prices via personal/
unofficial contact (indicating a buy-sell scam), or illegal online lending
offers** with the pattern: no collateral required, only ID card (KTP/KK)
needed, unreasonably low interest (e.g. <1%/month), instant disbursement,
contact only via personal WA/chat with no official OJK identity.

**Clear examples:**
- "Congratulations! Your number has won Rp50,000,000 from GoPay. Click the
  link below and enter your OTP code to claim: bit.ly/xxxxx"
- "Please confirm your ATM PIN to this number to verify your BCA account,
  which will otherwise be blocked"

### 2. PROMO_LEGIT
Official promotional/marketing messages that do NOT request sensitive data
(OTP, PIN, password) and do not pressure the recipient to click suspicious
links.

**Clear example:**
- "Enjoy 20% cashback on GoPay transactions at selected merchants today.
  Check the app for more details."

### 3. NORMAL
Ordinary personal/transactional messages, official notifications with no
suspicious elements, or everyday conversation.

**Clear example:**
- "Your transaction of Rp150,000 at Indomaret was successful. Your current
  balance is Rp850,000."

### 4. OTHER_SPAM
Spam/promotional messages that are NOT financially related (e-wallet, bank,
transactions, investment). Includes general service ads (shamans, herbal
remedies, etc.) and other non-financial spam.

**Clear example:**
- "TRUSTED SHAMAN SERVICES FOR BLACK MAGIC & LOVE SPELLS... Win Any Legal
  Case Call/WA xxx"

## Ambiguous Cases & How to Decide

| Case | Decision | Reasoning |
|---|---|---|
| A promotional message that asks the recipient to click a link for "account verification" | FRAUD_SCAM | Requesting verification via an external link is a common phishing pattern, even when framed as a promotion |
| A transaction notification with an implausible amount (e.g. Rp0 or negative) | FRAUD_SCAM | Amount anomalies are often an early indicator of a fake message |
| A message from an unknown contact inviting "high return" investment with no link | FRAUD_SCAM | Fraudulent investment schemes still fall into this category even without a link |
| An official promotion worded with strong urgency | PROMO_LEGIT (flag as `review_needed`) | Urgency alone isn't a strong indicator without a request for sensitive data — but should still be flagged for a second review |
| A "free for X days" promo with an automatic recurring charge afterward | FRAUD_SCAM | A hidden-fee/auto-subscribe trap counts as financial fraud even without an OTP request |
| High-value goods (electronics, etc.) sold far below fair market price, transacted via personal WA | FRAUD_SCAM | An unreasonable price combined with an unofficial channel is a classic buy-sell scam pattern |

## Known Limitations (from LLM-assisted labeling evaluation)

After the v1.3 guideline revision, the LLM (openai/gpt-oss-20b) achieved
93.85% accuracy against human labels. 4 remaining cases still differ:

1. The model is susceptible to **keyword bias**: messages mentioning "OTP"
   tend to be classified as FRAUD_SCAM even when the context is an official
   anti-phishing message (e.g. "Do not share this code with anyone"). The
   model appears to pattern-match on the keyword rather than understanding
   the sentence's actual intent.
2. The model is less consistent at detecting fraud disguised in official
   promotional formatting (real brand names such as "LAZADA", heavy
   uppercase/leetspeak formatting).
3. A supernatural-style testimonial case ("AKI JAGAT" etc.) sits in a gray
   area between FRAUD_SCAM and OTHER_SPAM, even for human annotators.

**Decision:** no further guideline revisions were made for these cases, to
avoid overfitting the guideline to a small sample (n=65). These cases are
documented as model limitations and directions for future work.

## Version & Revision History
- v1.0 (initial version)
- v1.0 → v1.1: added the OTHER_SPAM category after discovering the dataset
  contained non-financial spam that didn't fit the original 3 categories
  (fraud/promo/normal). This is consistent with the source dataset being
  general-purpose SMS spam rather than fintech-specific.
- v1.1 → v1.2: broadened the FRAUD_SCAM definition to cover hidden-fee
  subscription traps and unreasonably-priced buy-sell scams (found through
  Cohen's Kappa analysis of pass1 vs. pass2, kappa=0.901, 3 disagreement
  cases). Added a tense-based heuristic to distinguish NORMAL from
  PROMO_LEGIT.
- v1.2 → v1.3: added the illegal online lending pattern to the FRAUD_SCAM
  definition. Found through LLM-assisted labeling evaluation: the model
  (gpt-oss-20b) had a FRAUD_SCAM recall of only 0.72 because guideline v1.2
  didn't explicitly cover lending-scam patterns, despite them making up 40%
  of the dataset (26/65). The model misclassified 11 lending-scam cases as
  OTHER_SPAM.