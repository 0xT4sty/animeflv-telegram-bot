import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from commands import seguir, buscar, revisar_nuevos_episodios, handle_callback_query  # Importar el manejador de callback
from database import init_db
from logger import logger

# Cargar variables del archivo .env
load_dotenv()

TOKEN = os.getenv('TOKEN')

def main():
    logger.info("Iniciando el bot...")

    # Inicializamos la base de datos
    init_db()

    # Inicializamos el bot usando la nueva API de python-telegram-bot v20+
    application = Application.builder().token(TOKEN).build()

    # Añadimos los manejadores de comandos
    application.add_handler(CommandHandler("buscar", buscar))
    
    # Añadir CallbackQueryHandler para manejar las respuestas de los botones
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Iniciar la tarea de revisión cada 3 horas
    job_queue = application.job_queue
    job_queue.run_repeating(revisar_nuevos_episodios, interval=10800, first=0)

    # Empezamos a escuchar comandos
    logger.info("El bot está corriendo.")
    application.run_polling()

if __name__ == '__main__':
    main()

