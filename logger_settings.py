import os
import logging
from pathlib import Path
from datetime import datetime
from config import Config

class LoggingColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',        # Голубой
        'INFO': '\033[32m',         # Зеленый
        'WARNING': '\033[33m',      # Желтый
        'ERROR': '\033[31m',        # Красный
        'CRITICAL': '\033[1;31m'    # Жирный красный
    }
    RESET = '\033[0m'

    def format(self, record):
        # Создаем копию levelname, чтобы цвет не попадал в другие обработчики
        record.levelname_color = f"{self.COLORS.get(record.levelname, self.RESET)}{record.levelname}{self.RESET}"
        log_msg = super().format(record)
        return log_msg.replace(record.levelname, record.levelname_color)

logger = logging.getLogger("file_only_logger")

folder_logs = Path(Config.X_UI_LOGS_PATH)

if not folder_logs.is_dir():
    folder_logs.mkdir(parents=True, exist_ok=True)

# Форматирование имени файла с сегодняшней датой
log_filename = folder_logs / f'{datetime.now().strftime("%Y-%m-%d")}.log'

# File handler для записи в файл (без ANSI)
log_file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_file_handler.setFormatter(file_formatter)

# Добавляем только file handler
logger.addHandler(log_file_handler)

# Устанавливаем уровень логирования
logger.setLevel(logging.DEBUG)

logger.disabled = False