import logging
from datetime import datetime

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

logger = logging.getLogger("keyword_color_logger")

# Форматирование имени файла с сегодняшней датой
log_filename = f'logs/{datetime.now().strftime("%Y-%m-%d")}.log'

# Stream handler для консоли (цветной вывод)
console_handler = logging.StreamHandler()
console_formatter = LoggingColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# File handler для записи в файл (без ANSI)
log_file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_file_handler.setFormatter(file_formatter)

# Добавляем оба обработчика
logger.addHandler(console_handler)
logger.addHandler(log_file_handler)

# Устанавливаем уровень логирования
logger.setLevel(logging.DEBUG)

logger.disabled = False