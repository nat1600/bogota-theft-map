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
    try:
        with open('reportes.json', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([])  # Retorna array vacío si no existe el archivo

# =============== TELEGRAM BOT ===============

from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

load_dotenv()

# ¡IMPORTANTE! Usa variables de entorno para el token
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    print("⚠️  ERROR: No se encontró TELEGRAM_TOKEN en las variables de entorno")
    print("Crea un archivo .env con: TELEGRAM_TOKEN=tu_token_aqui")
    exit(1)

TIPO, LUGAR, HORA, UBICACION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚨 **SafeMap Bogotá Bot** 🚨\n\n"
        "Hola! Soy el bot para reportar robos en Bogotá.\n"
        "Tu reporte ayudará a mantener segura a la comunidad.\n\n"
        "¿Qué tipo de robo fue?\n"
        "_(Ejemplo: celular, bicicleta, cartera, etc.)_", 
        parse_mode='Markdown'
    )
    return TIPO

async def recibir_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tipo"] = update.message.text
    await update.message.reply_text(
        "📍 ¿Dónde ocurrió el robo?\n"
        "_(Ingresa la dirección, barrio o zona donde pasó)_",
        parse_mode='Markdown'
    )
    return LUGAR

async def recibir_lugar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lugar"] = update.message.text
    await update.message.reply_text(
        "🕐 ¿A qué hora aproximadamente ocurrió?\n"
        "_(Ejemplo: 18:30, 2:15 PM, tarde, etc.)_",
        parse_mode='Markdown'
    )
    return HORA

async def recibir_hora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hora"] = update.message.text
    await update.message.reply_text(
        "📍 Por último, necesito la ubicación exacta.\n\n"
        "Por favor envía tu ubicación usando el botón 📎 → 📍 Ubicación\n"
        "_(Esto nos permite marcar el punto exacto en el mapa)_",
        parse_mode='Markdown'
    )
    return UBICACION

async def recibir_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    if not location:
        await update.message.reply_text(
            "❌ No recibí una ubicación válida.\n"
            "Por favor, usa el botón de ubicación 📍"
        )
        return UBICACION

    # ✅ ESTRUCTURA CORREGIDA - Coincide con lo que espera map.js
    nuevo_reporte = {
        "lat": location.latitude,
        "lng": location.longitude,
        "barrio": context.user_data["lugar"],  # ✅ Cambio: lugar → barrio
        "hora": context.user_data["hora"],
        "detalle": f"Robo de {context.user_data['tipo']}",  # ✅ Nuevo: tipo → detalle
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "usuario": update.message.from_user.username or "anónimo",
        "timestamp": datetime.now().isoformat()  # Para ordenar por fecha
    }

    # Cargar reportes existentes
    try:
        with open("reportes.json", "r", encoding="utf-8") as f:
            reportes = json.load(f)
    except FileNotFoundError:
        reportes = []
    except json.JSONDecodeError:
        print("⚠️  Archivo reportes.json corrupto, creando nuevo")
        reportes = []

    # Añadir nuevo reporte
    reportes.append(nuevo_reporte)

    # Guardar con manejo de errores
    try:
        with open("reportes.json", "w", encoding="utf-8") as f:
            json.dump(reportes, f, indent=2, ensure_ascii=False)
        
        await update.message.reply_text(
            "✅ **¡Reporte enviado exitosamente!**\n\n"
            f"📋 **Resumen:**\n"
            f"• **Tipo:** {context.user_data['tipo']}\n"
            f"• **Lugar:** {context.user_data['lugar']}\n"
            f"• **Hora:** {context.user_data['hora']}\n"
            f"• **Fecha:** {nuevo_reporte['fecha']}\n\n"
            "🗺️ Tu reporte ya aparece en SafeMap Bogotá\n"
            "💙 ¡Gracias por ayudar a tu comunidad!\n\n"
            "_Escribe /start para hacer otro reporte_",
            parse_mode='Markdown'
        )
        
        print(f"✅ Nuevo reporte guardado: {context.user_data['tipo']} en {context.user_data['lugar']}")
        
    except Exception as e:
        print(f"❌ Error guardando reporte: {e}")
        await update.message.reply_text(
            "❌ Error al guardar el reporte. Inténtalo de nuevo más tarde."
        )

    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ **Reporte cancelado**\n\n"
        "Si quieres hacer un reporte, escribe /start",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 **Ayuda - SafeMap Bogotá Bot**\n\n"
        "**Comandos disponibles:**\n"
        "• /start - Iniciar nuevo reporte\n"
        "• /cancelar - Cancelar reporte actual\n"
        "• /ayuda - Mostrar esta ayuda\n\n"
        "**¿Cómo reportar?**\n"
        "1. Escribe /start\n"
        "2. Describe qué robaron\n"
        "3. Indica dónde pasó\n"
        "4. Di a qué hora\n"
        "5. Comparte tu ubicación 📍\n\n"
        "**¿Es seguro?**\n"
        "• Tu reporte es anónimo\n"
        "• Solo se guarda la ubicación del incidente\n"
        "• Ayudas a prevenir más robos\n\n"
        "_Tu seguridad es lo más importante_ 🛡️",
        parse_mode='Markdown'
    )

# Configurar bot
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Handler principal para reportes
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

# Añadir handlers
telegram_app.add_handler(conv_handler)
telegram_app.add_handler(CommandHandler("ayuda", ayuda))
telegram_app.add_handler(CommandHandler("help", ayuda))

# Funciones para ejecutar Flask y Bot
def run_flask():
    print("🌐 Flask corriendo en http://localhost:8000")
    flask_app.run(host='0.0.0.0', port=8000, debug=False)

def run_bot():
    print("🤖 Bot de Telegram iniciando...")
    print(f"🆔 Token configurado: {'✅ Sí' if TOKEN else '❌ No'}")
    
    try:
        telegram_app.run_polling()
    except Exception as e:
        print(f"❌ Error en el bot: {e}")
        print("Verifica que el token sea válido y tengas conexión a internet")

if __name__ == '__main__':
    print("🚀 Iniciando SafeMap Bogotá...")
    print("=" * 50)
    
    # Verificar que existe el directorio
    os.makedirs('js', exist_ok=True)
    
    # Verificar archivo reportes.json
    if not os.path.exists('reportes.json'):
        with open('reportes.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("📁 Archivo reportes.json creado")
    
    # Iniciar ambos servicios
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Bot en el hilo principal para poder parar con Ctrl+C
    run_bot()