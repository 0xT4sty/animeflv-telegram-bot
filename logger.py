import logging
import colorlog

# Definir los colores para el logger
log_colors = {
    'DEBUG': 'bold_blue',
    'INFO': 'bold_green',
    'WARNING': 'bold_yellow',
    'ERROR': 'bold_red',
    'CRITICAL': 'bold_red,bg_white',
}

# Crear un formateador con colores
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors=log_colors
)

# Configurar los handlers (archivo y consola)
file_handler = logging.FileHandler("bot.log")
console_handler = logging.StreamHandler()

# Aplicar el formateador solo al handler de consola (para ver colores en la terminal)
console_handler.setFormatter(formatter)

# Configurar el logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)
