import logging
from pathlib import Path
from datetime import datetime
from config import Config

class Logging_X_UI:
    logger = logging.getLogger("file_only_logger")

    folder_logs = Path(Config.X_UI_LOGS_PATH)

    if not folder_logs.is_dir():
        folder_logs.mkdir(parents=True, exist_ok=True)

    log_filename = folder_logs / f'{datetime.now().strftime("%Y-%m-%d")}.log'

    log_file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_file_handler.setFormatter(file_formatter)

    logger.addHandler(log_file_handler)

    logger.setLevel(logging.DEBUG)

    logger.disabled = False

logger_xui = Logging_X_UI.logger

class Logging_FastAPI:
    logger = logging.getLogger("fastapi")

    folder_logs = Path(Config.FAST_API_LOGS_PATH)

    if not folder_logs.is_dir():
        folder_logs.mkdir(parents=True, exist_ok=True)

    log_filename = folder_logs / f'{datetime.now().strftime("%Y-%m-%d")}.log'

    log_file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_file_handler.setFormatter(file_formatter)

    logger.addHandler(log_file_handler)

    logger.setLevel(logging.DEBUG)

    logger.disabled = False

logger_fastapi = Logging_FastAPI.logger


class Logging_Uvicorn:
    logger = logging.getLogger("uvicorn")

    folder_logs = Path(Config.UVICORN_LOGS_PATH)

    if not folder_logs.is_dir():
        folder_logs.mkdir(parents=True, exist_ok=True)

    log_filename = folder_logs / f'{datetime.now().strftime("%Y-%m-%d")}.log'

    log_file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_file_handler.setFormatter(file_formatter)

    logger.addHandler(log_file_handler)

    logger.setLevel(logging.DEBUG)

    logger.disabled = False
