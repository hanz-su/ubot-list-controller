#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uBot LIST Controller
Bot untuk manage trial/subscription uBot dengan OTP verification,
payment QRIS, dan referral system.

Developer: @PredikSpaceman
"""

import json
import os
import sys
import logging
import random
import string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

# ============ KONFIGURASI ============
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Ganti dengan token bot Anda
QRIS_STATIC = "00020126360014ID.CO.BRI.BRIMO0105026000031530010303UME51450015ID.OR.GPNQR.WWW011528160010A000000677010112
  "  # Ganti dengan QRIS static Anda
ADMIN_USERNAME = "@PredikSpaceman"
DATA_DIR = os.path.expanduser("~/ubot_controller_data")

# ============ SETUP DATA DIRECTORY ============
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ============ UTILITY FUNCTIONS ============

def get_user_file(user_id):
    """Dapatkan path file data user"""
    return os.path.join(DATA_DIR, f"user_{user_id}.json")

def load_user_data(user_id):
    """Load data user dari file"""
    file_path = get_user_file(user_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "user_id": user_id,
        "status": "none",  # none, trial, active, expired
        "trial_start": None,
        "trial_end": None,
        "subscription_start": None,
        "subscription_end": None,
        "ubot_name": None,
        "ubot_phone": None,
        "otp_code": None,
        "otp_attempts": 0,
        "referral_code": generate_referral_code(user_id),
        "referral_bonus_hours": 0,
        "referred_by": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payment_pending": False,
        "payment_amount": None,
        "payment_duration": None,
    }

def save_user_data(user_id, data):
    """Simpan data user ke file"""
    file_path = get_user_file(user_id)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")

def generate_otp():
    """Generate OTP 5 digit"""
    return ''.join(random.choices(string.digits, k=5))

def generate_referral_code(user_id):
    """Generate kode referral unik"""
    return f"REF{user_id}{random.randint(1000, 9999)}"

def generate_ubot_name(user_id):
    """Generate nama uBot otomatis"""
    return f"userbot_{random.randint(1000000, 9999999)}"

def calculate_remaining_time(end_time_str):
    """Hitung sisa waktu dalam format jam"""
    try:
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        remaining = end_time - datetime.now()
        if remaining.total_seconds() <= 0:
            return "Expired", 0
        hours = remaining.total_seconds() / 3600
        return f"{hours:.1f} jam", hours
    except:
        return "Unknown", 0

def format_time(hours):
    """Format durasi dalam jam menjadi string"""
    if hours == 1:
        return "1 Jam"
    elif hours == 3:
        return "3 Jam"
    elif hours == 7:
        return "7 Jam"
    elif hours == 14:
        return "14 Jam"
    elif hours == 30:
        return "30 Jam"
    else:
        return f"{hours}H"

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start - Menu utama"""
    if not update.message:
        return
    
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    
    # Load atau create user data
    user_data = load_user_data(user_id)
    save_user_data(user_id, user_data)
    
    menu_text = """🤖 uBot Controller

Menu utama:

1️⃣ Coba uBot gratis 24 jam
2️⃣ Hubungkan uBot setelah disetuiui/trial
3️⃣ Sewa/perpanjang uBot (chat manual)
4️⃣ Kode referral & klaim bonus jam
5️⃣ Cek status pendaftaran/trial
6️⃣ Manajemen uBot
7️⃣ Tutorial lengkap cara pakai uBot
8️⃣ Bantuan & daftar perintah
"""
    
    keyboard = [
        [InlineKeyboardButton("Coba uBot gratis 24 jam", callback_data="trial")],
        [InlineKeyboardButton("Hubungkan uBot", callback_data="connect")],
        [InlineKeyboardButton("Sewa/Perpanjang", callback_data="buy")],
        [InlineKeyboardButton("Kode Referral", callback_data="referral")],
        [InlineKeyboardButton("Cek Status", callback_data="status")],
        [InlineKeyboardButton("Manajemen uBot", callback_data="ubot_menu")],
        [InlineKeyboardButton("Tutorial", callback_data="tutor")],
        [InlineKeyboardButton("Bantuan", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def cmd_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /trial - Mulai trial 24 jam"""
    if not update.message:
        return
    
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    
    # Cek jika sudah trial/active
    if user_data["status"] in ["trial", "active"]:
        await update.message.reply_text(
            "⚠️ Kamu sudah memiliki trial/akses aktif!\n"
            "Ketik /status untuk cek status kamu."
        )
        return
    
    # Set status waiting_phone
    user_data["status"] = "waiting_phone"
    save_user_data(user_id, user_data)
    
    phone_keyboard = [
        [InlineKeyboardButton("📱 Kirim Nomor HP", callback_data="send_phone")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel_trial")],
    ]
    reply_markup = InlineKeyboardMarkup(phone_keyboard)
    
    await update.message.reply_text(
        "📱 <b>Mulai uBot Trial Gratis 24 Jam</b>\n\n"
        "Silakan kirim nomor HP Anda dengan format:\n"
        "<code>+628xxxxx</code>\n\n"
        "Atau klik tombol di bawah:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    
    context.user_data['waiting_phone'] = True

async def handle_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input nomor HP dari user"""
    if not update.message:
        return
    
    if not context.user_data.get('waiting_phone'):
        return
    
    user_id = update.message.from_user.id
    phone = update.message.text.strip()
    
    # Validasi format nomor
    if not phone.startswith('+62') or len(phone) < 10:
        await update.message.reply_text(
            "❌ Format nomor tidak valid!\n"
            "Gunakan format: <code>+628xxxxx</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    user_data = load_user_data(user_id)
    
    # Generate OTP
    otp = generate_otp()
    user_data["otp_code"] = otp
    user_data["ubot_phone"] = phone
    user_data["otp_attempts"] = 0
    save_user_data(user_id, user_data)
    
    otp_text = ' '.join(otp)  # Pisahkan tiap digit dengan spasi
    
    await update.message.reply_text(
        f"🔐 <b>Kode OTP sudah dikirim ke Telegram kamu</b>\n\n"
        f"Silakan kirim kode OTP dengan format:\n"
        f"(pisahkan setiap angka dengan spasi)\n\n"
        f"Contoh: <code>{otp_text}</code>\n\n"
        f"⚠️ Agar tidak diblokir Telegram:\n"
        f"Kirim kode OTP dengan spasi antar angka.",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data['waiting_otp'] = True
    context.user_data['waiting_phone'] = False

async def handle_otp_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle input OTP dari user"""
    if not update.message:
        return
    
    if not context.user_data.get('waiting_otp'):
        return
    
    user_id = update.message.from_user.id
    otp_input = update.message.text.strip().replace(' ', '')  # Hapus spasi
    
    user_data = load_user_data(user_id)
    
    # Cek OTP
    if otp_input != user_data["otp_code"]:
        user_data["otp_attempts"] += 1
        save_user_data(user_id, user_data)
        
        if user_data["otp_attempts"] >= 3:
            await update.message.reply_text(
                "❌ Kode OTP salah 3 kali!\n"
                "Ketik /trial untuk mulai ulang."
            )
            context.user_data['waiting_otp'] = False
            return
        
        await update.message.reply_text(
            f"❌ Kode OTP salah! Coba lagi.\n"
            f"Kesempatan tersisa: {3 - user_data['otp_attempts']}"
        )
        return
    
    # OTP benar - set trial
    now = datetime.now()
    trial_end = now + timedelta(hours=24)
    
    user_data["status"] = "trial"
    user_data["trial_start"] = now.strftime("%Y-%m-%d %H:%M:%S")
    user_data["trial_end"] = trial_end.strftime("%Y-%m-%d %H:%M:%S")
    user_data["ubot_name"] = generate_ubot_name(user_id)
    user_data["otp_code"] = None
    user_data["otp_attempts"] = 0
    save_user_data(user_id, user_data)
    
    # Format waktu akhir
    trial_end_str = trial_end.strftime("%d-%m-%Y %H:%M")
    
    success_text = f"""✅ <b>uBot Trial Aktif!</b>

uBot kamu berjalan dengan nama:
<code>{user_data['ubot_name']}</code>

🚨 Trial berlaku sampai: {trial_end_str} WIB (24 jam)

<b>Untuk lanjut pakai seterusnya setelah trial habis,</b>
chat manual {ADMIN_USERNAME} untuk membeli akses Userbot.

📚 <b>Tutorial Menggunakan uBot:</b>
1. Ketik <code>.akses</code> lalu <code>.on</code> di grup untuk mengaktifkan uBot
2. Ketik <code>.cmd</code> untuk lihat daftar perintah
3. Ketik <code>.tutor</code> untuk panduan lengkap
"""
    
    await update.message.reply_text(success_text, parse_mode=ParseMode.HTML)
    context.user_data['waiting_otp'] = False

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /status - Cek status trial/subscription"""
    if not update.message:
        return
    
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    
    status = user_data["status"]
    
    if status == "none":
        text = f"""❌ <b>Status: Belum Trial</b>

Kamu belum memiliki akses uBot.
Ketik /trial untuk mulai gratis 24 jam.
"""
    elif status == "trial":
        remaining_text, remaining_hours = calculate_remaining_time(user_data["trial_end"])
        trial_start = user_data["trial_end"]
        
        text = f"""🎁 <b>Status: Trial</b>

📅 Disetuiui: {user_data['trial_start']}
⏱️ Sisa waktu: {remaining_text}

<b>Kelola uBot:</b>
/ubot stop — matikan uBot
/ubot start — nyalakan uBot

<b>Kalau uBot tidak merespon di grup:</b>
1️⃣ Ketik <code>.akses</code> di grup dulu
2️⃣ Lalu ketik <code>.on</code> buat nyalain
"""
    elif status == "active":
        remaining_text, remaining_hours = calculate_remaining_time(user_data["subscription_end"])
        
        text = f"""✅ <b>Status: Active/Langganan</b>

📅 Terdaftar: {user_data['subscription_start']}
⏱️ Sisa waktu: {remaining_text}

<b>Kelola uBot:</b>
/ubot stop — matikan uBot
/ubot start — nyalakan uBot
/connect — hubungkan ulang jika session expired

<b>Kalau uBot tidak merespon di grup:</b>
1️⃣ Ketik <code>.akses</code> di grup dulu
2️⃣ Lalu ketik <code>.on</code> buat nyalain
"""
    else:  # expired
        text = f"""⏰ <b>Status: Expired</b>

Akses uBot kamu sudah habis.
Ketik /buy untuk perpanjang akses.
"""
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def cmd_connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /connect - Hubung ulang session"""
    if not update.message:
        return
    
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    
    if user_data["status"] == "none":
        await update.message.reply_text(
            "❌ Kamu belum memiliki akses uBot!\n"
            "Ketik /trial untuk coba gratis 24 jam."
        )
        return
    
    # Reset OTP dan minta input baru
    user_data["status"] = "waiting_phone_connect"
    save_user_data(user_id, user_data)
    
    await update.message.reply_text(
        "🔄 <b>Hubungkan Ulang uBot</b>\n\n"
        "Session kamu sudah tidak valid lagi.\n"
        "Kamu akan login ulang dengan OTP baru.\n\n"
        "📱 Kirim nomor HP Anda:\n"
        "<code>+628xxxxx</code>",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data['waiting_phone'] = True

async def cmd_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /buy - Menu beli/perpanjang akses"""
    if not update.message:
        return
    
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    
    buy_text = f"""💰 <b>Beli/Perpanjang Akses uBot</b>

<b>Paket Tersedia:</b>
"""
    
    # Tombol paket
    keyboard = [
        [InlineKeyboardButton("1 Jam - Rp 6.000", callback_data="buy_1h"),
         InlineKeyboardButton("3 Jam - Rp 18.000", callback_data="buy_3h")],
        [InlineKeyboardButton("7 Jam - Rp 42.000", callback_data="buy_7h"),
         InlineKeyboardButton("14 Jam - Rp 84.000", callback_data="buy_14h")],
        [InlineKeyboardButton("30 Jam - Rp 180.000", callback_data="buy_30h")],
        [InlineKeyboardButton("💬 Chat Manual ke Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(buy_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback dari inline buttons"""
    query = update.callback_query
    user_id = query.from_user.id
    user_data = load_user_data(user_id)
    
    await query.answer()
    
    # Handle menu buttons
    if query.data == "trial":
        await query.edit_message_text(
            "📱 <b>Mulai uBot Trial Gratis 24 Jam</b>\n\n"
            "Silakan kirim nomor HP Anda dengan format:\n"
            "<code>+628xxxxx</code>",
            parse_mode=ParseMode.HTML
        )
        user_data["status"] = "waiting_phone"
        save_user_data(user_id, user_data)
        context.user_data['waiting_phone'] = True
    
    elif query.data == "connect":
        await query.edit_message_text(
            "🔄 <b>Hubungkan Ulang uBot</b>\n\n"
            "Session kamu sudah tidak valid lagi.\n"
            "Kamu akan login ulang dengan OTP baru.\n\n"
            "📱 Kirim nomor HP Anda:\n"
            "<code>+628xxxxx</code>",
            parse_mode=ParseMode.HTML
        )
        user_data["status"] = "waiting_phone_connect"
        save_user_data(user_id, user_data)
        context.user_data['waiting_phone'] = True
    
    elif query.data == "status":
        if user_data["status"] == "trial":
            remaining_text, _ = calculate_remaining_time(user_data["trial_end"])
            text = f"""🎁 <b>Status: Trial</b>

📅 Disetuiui: {user_data['trial_start']}
⏱️ Sisa waktu: {remaining_text}
"""
        elif user_data["status"] == "active":
            remaining_text, _ = calculate_remaining_time(user_data["subscription_end"])
            text = f"""✅ <b>Status: Active</b>

📅 Terdaftar: {user_data['subscription_start']}
⏱️ Sisa waktu: {remaining_text}
"""
        else:
            text = "❌ <b>Status: Belum Trial</b>\n\nKetik /trial untuk mulai gratis."
        
        await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    
    elif query.data == "referral":
        text = f"""🎁 <b>Kode Referral Kamu</b>

<code>{user_data['referral_code']}</code>

📊 <b>Statistik Referral:</b>
Bonus jam terkumpul: {user_data['referral_bonus_hours']} jam

Ajak teman gunakan kode referral kamu,
setiap referral yang berhasil = +1 jam bonus!
"""
        await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    
    elif query.data == "ubot_menu":
        text = f"""⚙️ <b>Manajemen uBot</b>

<b>uBot kamu:</b>
Nama: <code>{user_data['ubot_name'] or 'Belum diset'}</code>
Status: {user_data['status']}

<b>Perintah:</b>
/ubot — lihat detail uBot
/ubot start — nyalakan
/ubot stop — matikan
/connect — hubung ulang session
"""
        await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    
    elif query.data == "tutor":
        tutor_text = """📚 <b>Tutorial uBot LIST</b>

<b>Apa itu uBot?</b>
uBot adalah akun Telegram kamu yang dijalankan sebagai bot pencatat bet di grup. Bot ini otomatis mencatat siapa pasang K (Kecil) atau B (Besar).

<b>Langkah-Langkah:</b>

1️⃣ <b>Mulai Gratis</b>
Ketik /trial → Tidak ada approval → Kirim nomor HP → Kirim kode OTP → uBot langsung jalan. Trial 24 jam.

2️⃣ <b>Kalau Proses Putus</b>
Ketik /connect untuk lanjut dari langkah terakhir.

3️⃣ <b>Aktifkan di Grup</b>
Masukkan uBot ke grup, lalu ketik <code>.akses</code> di grup tersebut.

4️⃣ <b>Nyalakan Bot</b>
Ketik <code>.on</code> di grup → bot mulai terima input bet.

<b>Perintah di Grup:</b>
<code>.on</code> / <code>.off</code> — aktif/nonaktif
<code>K5</code> / <code>B10</code> — pasang K/B
<code>.list</code> — lihat daftar bet
<code>.cmd</code> — semua perintah
"""
        await query.edit_message_text(tutor_text, parse_mode=ParseMode.HTML)
    
    elif query.data == "help":
        help_text = f"""❓ <b>Bantuan & Daftar Perintah</b>

<b>Perintah Utama:</b>
/start — Menu utama
/trial — Coba uBot gratis 24 jam
/status — Cek status
/connect — Hubung ulang
/buy — Beli/perpanjang
/referral — Kode referral
/ubot — Kelola uBot
/tutor — Tutorial
/help — Bantuan

<b>Masih ada pertanyaan?</b>
Hubungi: {ADMIN_USERNAME}
"""
        await query.edit_message_text(help_text, parse_mode=ParseMode.HTML)
    
    # Handle buy buttons
    elif query.data.startswith("buy_"):
        duration_map = {
            "buy_1h": (1, 6000),
            "buy_3h": (3, 18000),
            "buy_7h": (7, 42000),
            "buy_14h": (14, 84000),
            "buy_30h": (30, 180000),
        }
        
        hours, amount = duration_map[query.data]
        user_data["payment_pending"] = True
        user_data["payment_amount"] = amount
        user_data["payment_duration"] = hours
        save_user_data(user_id, user_data)
        
        payment_text = f"""💳 <b>Konfirmasi Pembayaran</b>

<b>Paket:</b> {format_time(hours)}
<b>Harga:</b> Rp {amount:,}

<b>Cara Pembayaran:</b>
1️⃣ Scan QRIS di bawah
2️⃣ Lakukan pembayaran
3️⃣ Chat admin {ADMIN_USERNAME} dengan bukti pembayaran

<b>Catatan:</b>
Setelah pembayaran, admin akan approve dan akses Anda langsung aktif.
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Kirim Bukti Pembayaran", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("❌ Batal", callback_data="cancel_payment")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(payment_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    elif query.data == "cancel_payment":
        user_data["payment_pending"] = False
        save_user_data(user_id, user_data)
        await query.edit_message_text("❌ Pembayaran dibatalkan.")
    
    elif query.data == "cancel_trial":
        await query.edit_message_text("❌ Trial dibatalkan.")
    
    elif query.data == "send_phone":
        await query.edit_message_text(
            "📱 Silakan kirim nomor HP Anda:\n"
            "<code>+628xxxxx</code>",
            parse_mode=ParseMode.HTML
        )

async def cmd_ubot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /ubot - Kelola uBot"""
    if not update.message:
        return
    
    user_id = update.message.from_user.id
    user_data = load_user_data(user_id)
    args = update.message.text.split()
    
    if len(args) == 1:
        # /ubot - tampilkan status
        text = f"""🌐 <b>Status uBot</b>

Nama PM2: <code>{user_data['ubot_name'] or 'Belum diset'}</code>
Status: 🟢 Online
Phone: <code>{user_data['ubot_phone'] or 'Belum diset'}</code>
Session: ✅ Ada
Terhubung sejak: {user_data['trial_start'] or user_data['subscription_start'] or 'N/A'} WIB

<b>Perintah:</b>
/ubot start — nyalakan uBot
/ubot stop — matikan uBot
/connect — hubung ulang session
"""
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    elif len(args) > 1:
        command = args[1]
        
        if command == "start":
            await update.message.reply_text(
                "✅ <b>uBot Dinyalakan</b>\n\n"
                "Bot sudah siap di grup. Ketik <code>.on</code> di grup untuk aktifkan.",
                parse_mode=ParseMode.HTML
            )
        elif command == "stop":
            await update.message.reply_text(
                "🛑 <b>uBot Dimatikan</b>\n\n"
                "Bot akan berhenti menerima input. Ketik <code>.on</code> untuk nyalakan lagi.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text("❌ Perintah tidak dikenal.")

async def cmd_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /tutor - Tutorial lengkap"""
    if not update.message:
        return
    
    tutor_text = """📚 <b>Tutorial Menggunakan uBot LIST</b>

<b>Apa itu uBot?</b>
uBot adalah akun Telegram kamu yang dijalankan sebagai bot pencatat bet di grup. Bot ini otomatis mencatat siapa pasang K (Kecil) atau B (Besar).

<b>LANGKAH 1 — Mulai Gratis</b>
Ketik /trial → Bot langsung minta nomor HP → Kirim kode OTP → uBot langsung jalan di background. Trial berlaku 24 jam.

<b>LANGKAH 2 — Kalau Proses Kepotong</b>
Belum sempat kirim nomor HP/OTP sampai selesai? Ketik /connect untuk melanjutkan dari langkah terakhir.

<b>LANGKAH 3 — Aktifkan di Grup</b>
Masukkan uBot ke grup, lalu ketik <code>.akses</code> di grup tersebut.
Bot mulai memantau pesan K/B di grup itu.

<b>LANGKAH 4 — Nyalakan Bot</b>
Ketik <code>.on</code> di grup → bot mulai menerima input bet.

<b>PERINTAH DASAR di Grup (pakai titik):</b>
• <code>.on</code> / <code>.off</code> — aktifkan/nonaktifkan
• <code>K5</code> / <code>B10</code> — pasang Kecil/Besar
• <code>.list</code> — lihat daftar bet ronde ini
• <code>.resetlist</code> / <code>.rs</code> — kosongkan daftar
• <code>.cmd</code> — semua perintah tersedia
• <code>.tutor</code> — tutorial lengkap di grup

<b>MANAJEMEN uBot (dari sini):</b>
• /ubot — lihat status uBot
• /ubot start — nyalakan uBot
• /ubot stop — matikan uBot
• /connect — hubungkan ulang jika session expired

<b>Kalau Trial/Langganan Habis:</b>
Ketik /buy → chat manual ke @PredikSpaceman buat sewa/perpanjang akses uBot.

❓ Butuh bantuan? Hubungi @PredikSpaceman
"""
    
    await update.message.reply_text(tutor_text, parse_mode=ParseMode.HTML)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /help - Bantuan"""
    if not update.message:
        return
    
    help_text = f"""❓ <b>Bantuan & Daftar Perintah</b>

<b>🤖 Perintah Utama:</b>
/start — Menu utama
/trial — Coba uBot gratis 24 jam
/status — Cek status pendaftaran/trial
/connect — Hubungkan ulang jika proses terputus
/buy — Sewa/perpanjang akses
/referral — Kode referral & klaim bonus
/ubot — Manajemen uBot
/tutor — Tutorial lengkap
/help — Bantuan (pesan ini)

<b>📝 Perintah di Grup (pakai titik):</b>
.on / .off — aktif/nonaktif
K5 / B10 — pasang K/B
.list — lihat daftar
.cmd — semua perintah
.tutor — tutorial

<b>💬 Hubungi Developer:</b>
{ADMIN_USERNAME} — Untuk pertanyaan & bantuan
"""
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

def main():
    """Main function"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Ganti BOT_TOKEN dengan token bot Anda!")
        print("Cara mendapat token:")
        print("1. Chat @BotFather di Telegram")
        print("2. Ketik /newbot")
        print("3. Ikuti instruksi")
        sys.exit(1)
    
    # Buat aplikasi
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trial", cmd_trial))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("connect", cmd_connect))
    app.add_handler(CommandHandler("buy", cmd_buy))
    app.add_handler(CommandHandler("ubot", cmd_ubot))
    app.add_handler(CommandHandler("tutor", cmd_tutor))
    app.add_handler(CommandHandler("help", cmd_help))
    
    # Callback query handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handlers
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_phone_input
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_otp_input
    ))
    
    print("🤖 uBot LIST Controller sedang berjalan...")
    print("Tekan Ctrl+C untuk berhenti")
    
    # Jalankan bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✅ Bot dihentikan")
    except Exception as e:
        print(f"\n❌ Error: {e}")
