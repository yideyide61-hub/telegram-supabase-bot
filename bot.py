import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
from supabase import create_client
import datetime

# === Load environment variables ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# === Supabase client ===
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# === Telegram bot setup ===
app = Flask(__name__)
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("✅ Bot started! Use /log to save activity.")

async def log(update: Update, context):
    user = update.message.from_user
    now = datetime.datetime.utcnow()

    supabase.table("activities").insert({
        "user_id": str(user.id),
        "username": user.username or user.full_name,
        "action": "custom action",
        "start_time": now.isoformat(),
        "end_time": (now + datetime.timedelta(hours=1)).isoformat(),
        "duration_seconds": 3600,
        "chat_id": update.message.chat_id
    }).execute()

    await update.message.reply_text("✅ Activity saved to Supabase!")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("log", log))

# === Flask route for Telegram Webhook ===
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok", 200

# === Health check route ===
@app.route("/")
def index():
    return "Bot is alive!"

