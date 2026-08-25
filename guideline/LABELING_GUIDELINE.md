# FinText-QC Labeling Guideline v1.0

## Tujuan
Mengklasifikasikan pesan SMS/chat berbahasa Indonesia ke dalam kategori terkait
risiko penipuan finansial, untuk simulasi use-case trust & safety pada platform
pembayaran digital.

## Kategori Label

### 1. FRAUD_SCAM
Pesan yang mengandung indikasi penipuan finansial: permintaan transfer dengan
embel-embel hadiah/undian, phishing (minta OTP/PIN/kode verifikasi), 
mengaku dari bank/e-wallet resmi tapi minta data sensitif, link mencurigakan
dengan iming-iming uang.

**Contoh jelas:**
- "Selamat! Nomor anda mendapatkan hadiah Rp50.000.000 dari GoPay. Klik link
  berikut dan masukkan kode OTP anda untuk klaim: bit.ly/xxxxx"
- "Mohon konfirmasi PIN ATM Anda ke nomor ini untuk verifikasi akun BCA yang
  akan diblokir"

### 2. PROMO_LEGIT
Pesan promosi/marketing resmi yang TIDAK meminta data sensitif (OTP, PIN,
password) dan tidak memaksa klik link mencurigakan.

**Contoh jelas:**
- "Nikmati cashback 20% untuk transaksi GoPay di merchant pilihan hari ini.
  Cek aplikasi untuk info lebih lanjut."

### 3. NORMAL
Pesan personal/transaksional biasa, notifikasi resmi tanpa unsur mencurigakan,
atau obrolan sehari-hari.

**Contoh jelas:**
- "Transaksi Anda sebesar Rp150.000 di Indomaret berhasil. Saldo Anda saat
  ini Rp850.000."

## Kasus Ambigu & Cara Memutuskan

| Kasus | Keputusan | Alasan |
|---|---|---|
| Pesan promo tapi minta klik link untuk "verifikasi akun" | FRAUD_SCAM | Permintaan verifikasi via link eksternal adalah pola phishing umum, meski dibungkus promo |
| Notifikasi transaksi tapi nominal tidak masuk akal (misal Rp0 atau minus) | FRAUD_SCAM | Anomali nominal sering jadi indikator awal pesan palsu |
| Pesan dari kontak tidak dikenal berisi ajakan investasi "untung besar" tanpa link | FRAUD_SCAM | Skema investasi bodong tetap masuk kategori ini walau tanpa link |
| Promo resmi tapi bahasa terkesan "terlalu mendesak" (urgency tinggi) | PROMO_LEGIT (tandai sebagai `review_needed`) | Urgency saja bukan indikator kuat tanpa permintaan data sensitif — tapi tetap ditandai untuk review kedua |

## Versi & Riwayat Revisi
- v1.0 25-agustus-2025 — versi awal
- *(akan diupdate di Tahap 4 setelah analisis disagreement)*
