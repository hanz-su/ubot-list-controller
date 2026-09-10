# uBot LIST Controller

🤖 Telegram Bot untuk manage trial/subscription uBot dengan OTP verification, payment QRIS, dan referral system.

## Fitur Utama

✅ **Trial 24 Jam Gratis**
- Auto generate uBot setiap user
- OTP verification via Telegram
- Countdown timer 24 jam

✅ **Payment System**
- Paket: 1H, 3H, 7H, 14H, 30H
- Payment via QRIS static
- Manual approval dari admin

✅ **Referral System**
- Auto generate unique referral code per user
- Bonus jam untuk setiap referral yang berhasil
- Tracking referral statistics

✅ **User Management**
- Status tracking (none, trial, active, expired)
- Auto login via OTP
- Session management (/connect untuk restart)

✅ **Command Group**
- Integrasi dengan uBot di grup
- Perintah: .on, .off, .list, .cmd, .tutor, dll
- Anti-clone feature (mention biru otomatis)

## Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/hanz-su/ubot-list-controller.git
cd ubot-list-controller
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Bot Token
```bash
# Edit ubot_controller.py
# Ganti: BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
# Dengan token bot Anda dari @BotFather
```

### 4. Setup QRIS
```bash
# Edit ubot_controller.py
# Ganti: QRIS_STATIC = "..."
# Dengan QRIS static Anda dari bank
```

### 5. Jalankan Bot
```bash
python3 ubot_controller.py
```

## Command List

### User Commands
```
/start       — Menu utama
/trial       — Mulai trial 24 jam gratis
/status      — Cek status akses
/connect     — Hubung ulang session
/buy         — Beli/perpanjang akses
/referral    — Kode referral & bonus
/ubot        — Kelola uBot
/tutor       — Tutorial lengkap
/help        — Bantuan
```

### Group Commands (dengan titik)
```
.on / .off   — Aktifkan/nonaktifkan bot
K5 / B10     — Pasang Kecil/Besar
.list        — Lihat daftar bet
.resetlist   — Reset daftar bet
.cmd         — Lihat semua perintah
.tutor       — Tutorial
```

## Directory Structure

```
ubot-list-controller/
├── ubot_controller.py          # Main bot script
├── requirements.txt            # Python dependencies
├── README.md                   # Dokumentasi
└── ~/ubot_controller_data/     # User data storage (auto-created)
    ├── user_123456789.json     # User data per ID
    └── ...
```

## Data Structure

### User Data (user_ID.json)
```json
{
  "user_id": 123456789,
  "status": "trial",
  "trial_start": "2026-09-11 21:48:00",
  "trial_end": "2026-09-12 21:48:00",
  "subscription_start": null,
  "subscription_end": null,
  "ubot_name": "userbot_7075839329",
  "ubot_phone": "+6289999999999",
  "otp_code": null,
  "referral_code": "REF1234567890",
  "referral_bonus_hours": 0,
  "referred_by": null,
  "created_at": "2026-09-11 21:48:00"
}
```

## Configuration

Edit di `ubot_controller.py`:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"      # Token dari @BotFather
QRIS_STATIC = "00020126..."            # QRIS dari bank Anda
ADMIN_USERNAME = "@PredikSpaceman"     # Username admin
DATA_DIR = "~/ubot_controller_data"    # Folder penyimpanan data
```

## Payment Pricing

| Paket | Harga | Duration |
|-------|-------|----------|
| 1 Jam | Rp 6.000 | 1H |
| 3 Jam | Rp 18.000 | 3H |
| 7 Jam | Rp 42.000 | 7H |
| 14 Jam | Rp 84.000 | 14H |
| 30 Jam | Rp 180.000 | 30H |
| Flat | Rp 6.000/hari | Max 30 hari |

## Flow Diagram

### Trial Flow
```
/trial → Kirim Phone → Generate OTP → Verify OTP → Set Trial 24H → Active
```

### Payment Flow
```
/buy → Pilih Paket → Scan QRIS → Kirim Bukti ke Admin → Approve → Active
```

### Connect Flow
```
/connect → Kirim Phone Baru → Generate OTP Baru → Verify → Reconnect
```

## Fitur Anti-Clone

Untuk mengaktifkan di grup:
```
.mode bot
```

Nama pemain akan otomatis menjadi mention biru yang ter-link ke akun Telegram asli.

**Keuntungan:**
- Admin tidak perlu tag manual satu-satu saat WD
- Akun clone/palsu ketauan langsung karena ID Telegram-nya beda
- Lebih aman & cepat

## Troubleshooting

### Bot tidak merespon
1. Cek token bot sudah benar
2. Pastikan bot sudah ditambah ke grup
3. Ketik `.akses` di grup dulu
4. Ketik `.on` untuk nyalakan bot

### OTP tidak masuk
1. Pastikan nomor HP sudah benar (format: +62)
2. Tunggu beberapa detik setelah kirim nomor
3. Coba `/connect` jika timeout

### Trial/Session Expired
Ketik `/connect` untuk hubung ulang dengan OTP baru.

## Support

❓ Pertanyaan atau bug? Hubungi:
- **@PredikSpaceman** - Admin
- **@Angga Official** - Developer

## License

MIT License - Bebas digunakan untuk keperluan pribadi & komersial

## Changelog

### v1.0.0 (2026-09-11)
- Initial release
- Trial 24 jam dengan OTP
- Payment system QRIS
- Referral system
- User management
- Group command integration
