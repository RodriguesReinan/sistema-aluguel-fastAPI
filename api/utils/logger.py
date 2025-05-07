import logging
from logging.handlers import RotatingFileHandler
import os

# Garante que o diretório de tables_logs exista
os.makedirs("tables_logs", exist_ok=True)

# Configuração básica
logger = logging.getLogger("scheduler_logger")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("tables_logs/scheduler.log", maxBytes=1_000_000, backupCount=3)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
