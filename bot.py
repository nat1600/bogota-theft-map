import json
from datetime import datetime
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Obtener el token desde el archivo .env
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Estados de la conversación
TIPO, LUGAR, HORA, UBICACION = range(4)

reportes = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋 Soy el bot para reportar robos en Bogotá.\n¿Qué tipo de robo fue? (ej: celular, bici, etc.)")
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

app = ApplicationBuilder().token(TOKEN).build()

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

app.add_handler(conv_handler)

print("🤖 Bot corriendo...")

app.run_polling()
