import telebot
from telebot import types
from yt_dlp import YoutubeDL
import re
import os

API_TOKEN = "8252876339:AAFQAJ2lFTfIhPh8w7DxorHxOHSYJc5YJD0"
bot = telebot.TeleBot(API_TOKEN)

ADMIN_USERNAME = '@cold_reactions'

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
    bot.send_message(message.chat.id, "🤖 Bot ishga tushdi!\nMusiqa nomi yoki ssilka yuboring.", reply_markup=markup)

#oydalanuvchi xabarini qabul qilish
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text.strip()
    if re.match(r'https?://(www\.)?instagram\.com/.+', text) or re.match(r'https?://(www\.)?youtube\.com/.+', text) or re.match(r'https?://youtu\.be/.+', text):
        url = text
    else:
        url = f"ytsearch1:{text}"  # Musiqa nomi bo‘lsa avtomatik qidirish
    send_inline_options(message, url)

def send_inline_options(message, url):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📹 Video", callback_data=f"video|{url}"))
    markup.add(types.InlineKeyboardButton("🎵 Audio", callback_data=f"audio|{url}"))
    bot.send_message(message.chat.id, "Nimani yuklamoqchisiz?", reply_markup=markup)

# Inline tugma bosilganda
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        action, url = call.data.split("|", 1)
        bot.answer_callback_query(call.id, text="Yuklanmoqda...⏳")

        filename = None
        ydl_opts = {}

        if action == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            ydl_opts = {
                'format': 'best',
                'noplaylist': True,
                'quiet': True,
                'outtmpl': '%(title)s.%(ext)s',
            }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if action == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
                if os.path.getsize(filename) > 50*1024*1024:
                    bot.send_message(call.message.chat.id, "⚠️ Audio fayl juda katta!")
                bot.send_audio(call.message.chat.id, open(filename, 'rb'))
            else:
                if os.path.getsize(filename) > 50*1024*1024:
                    bot.send_message(call.message.chat.id, "⚠️ Video fayl juda katta!")
                bot.send_video(call.message.chat.id, open(filename, 'rb'))

        if filename and os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xatolik yuz berdi: {str(e)}")

bot.infinity_polling()
