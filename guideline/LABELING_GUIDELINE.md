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
dengan iming-iming uang, **skema biaya tersembunyi/auto-subscribe berkedok
gratis (RBT, konten premium, dll), atau penawaran barang bernilai tinggi
dengan harga tidak masuk akal via kontak pribadi/non-resmi (indikasi
penipuan jual-beli).**

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

### 4. OTHER_SPAM
Pesan yang bersifat spam/promosi tapi TIDAK terkait finansial (e-wallet, bank,
transaksi, investasi). Termasuk iklan jasa umum (dukun, obat, dll), spam
non-finansial lainnya.

**Contoh jelas:**
- "JASA DUKUN SANTET & PELET RESMI TERPERCAYA... Menang Perkara Tlp/Wa. xxx"

## Kasus Ambigu & Cara Memutuskan

| Kasus | Keputusan | Alasan |
|---|---|---|
| Pesan promo tapi minta klik link untuk "verifikasi akun" | FRAUD_SCAM | Permintaan verifikasi via link eksternal adalah pola phishing umum, meski dibungkus promo |
| Notifikasi transaksi tapi nominal tidak masuk akal (misal Rp0 atau minus) | FRAUD_SCAM | Anomali nominal sering jadi indikator awal pesan palsu |
| Pesan dari kontak tidak dikenal berisi ajakan investasi "untung besar" tanpa link | FRAUD_SCAM | Skema investasi bodong tetap masuk kategori ini walau tanpa link |
| Promo resmi tapi bahasa terkesan "terlalu mendesak" (urgency tinggi) | PROMO_LEGIT (tandai sebagai `review_needed`) | Urgency saja bukan indikator kuat tanpa permintaan data sensitif — tapi tetap ditandai untuk review kedua |
| Promo "gratis Xhari" tapi ada skema tarif berlanjut otomatis setelahnya | FRAUD_SCAM | Hidden fee/auto-subscribe trap = penipuan finansial meski tidak minta OTP |
| Barang bernilai tinggi (elektronik dll) dijual jauh di bawah harga pasar wajar, transaksi via WA pribadi | FRAUD_SCAM | Harga tidak masuk akal + channel non-resmi = pola scam jual-beli klasik |

## Versi & Riwayat Revisi
- v1.0 25-agustus-2025 — versi awal
- v1.0 → v1.1: menambah kategori OTHER_SPAM setelah menemukan dataset berisi
  spam non-finansial yang tidak fit ke 3 kategori awal (fraud/promo/normal).
  Ini konsisten dengan sifat dataset sumber yang general-purpose SMS spam,
  bukan spesifik fintech.
  - v1.1 → v1.2: memperluas definisi FRAUD_SCAM mencakup hidden-fee subscription
  trap dan scam jual-beli harga tidak wajar (ditemukan dari analisis Cohen's
  Kappa pass1 vs pass2, kappa=0.901, 3 disagreement cases). Menambahkan
  heuristik tense-based untuk membedakan NORMAL vs PROMO_LEGIT.
