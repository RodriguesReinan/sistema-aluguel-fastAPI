import logging
from logging.handlers import RotatingFileHandler
import os

# Garante que o diretório de logs exista
os.makedirs("logs", exist_ok=True)

# Configuração básica
logger = logging.getLogger("scheduler_logger")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("logs/scheduler.log", maxBytes=1_000_000, backupCount=3)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
