from flask import Flask, send_from_directory, jsonify
from threading import Thread
import json
import asyncio
import os

# =============== FLASK APP ===============

flask_app = Flask(__name__, static_folder='.')

@flask_app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@flask_app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('./js', path)

@flask_app.route('/reportes.json')
def reportes():
    with open('reportes.json', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

# =============== TELEGRAM BOT ===============

from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

TIPO, LUGAR, HORA, UBICACION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola 👋 Soy el bot para reportar robos en Bogotá.\n¿Qué tipo de robo fue? (ej: celular, bici, etc.)")
    return TIPO

async def recibir_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tipo"] = update.message.text
    await update.message.reply_text("¿Dónde ocurrió el robo? (dirección o zona)")
    return LUGAR

async def recibir_lugar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lugar"] = update.message.text
    await update.message.reply_text("¿A qué hora ocurrió? (ej: 18:30)")
    return HORA

async def recibir_hora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hora"] = update.message.text
    await update.message.reply_text("Por favor, envíame tu ubicación 📍 (usa la opción del clip)")
    return UBICACION

async def recibir_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    if not location:
        await update.message.reply_text("Debes enviar una ubicación válida.")
        return UBICACION

    data = {
        "lat": location.latitude,
        "lng": location.longitude,
        "tipo": context.user_data["tipo"],
        "lugar": context.user_data["lugar"],
        "hora": context.user_data["hora"],
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "usuario": update.message.from_user.username or "anónimo"
    }

    try:
        with open("reportes.json", "r", encoding="utf-8") as f:
            reportes = json.load(f)
    except FileNotFoundError:
        reportes = []

    reportes.append(data)

    with open("reportes.json", "w", encoding="utf-8") as f:
        json.dump(reportes, f, indent=2, ensure_ascii=False)

    await update.message.reply_text("✅ Robo reportado. ¡Gracias por tu ayuda!")
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelado. Si quieres empezar de nuevo, escribe /start")
    return ConversationHandler.END

telegram_app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_tipo)],
        LUGAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_lugar)],
        HORA: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_hora)],
        UBICACION: [MessageHandler(filters.LOCATION, recibir_ubicacion)],
    },
    fallbacks=[CommandHandler("cancelar", cancelar)]
)

telegram_app.add_handler(conv_handler)



def run_flask():
    print("🌐 Flask corriendo en http://localhost:8000")
    flask_app.run(host='0.0.0.0', port=8000)

def run_bot():
    print("🤖 Bot corriendo...")

    loop = asyncio.new_event_loop()         # ⏺️ 1) Crea nuevo event loop
    asyncio.set_event_loop(loop)            # ⏺️ 2) Asigna como loop actual

    loop.run_until_complete(telegram_app.run_polling()) 

if __name__ == '__main__':
    Thread(target=run_flask).start()
    run_bot()
