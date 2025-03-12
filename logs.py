import logging as log
from logging.handlers import TimedRotatingFileHandler

log.basicConfig(
	level=log.WARNING,
	format="%(asctime)s - %(levelname)s - %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
	handlers=[
		log.StreamHandler(),  # Вывод в консоль
		TimedRotatingFileHandler(
			filename="app.log",  # Базовое имя файла
			when="midnight",  # Интервал: каждый день в полночь
			interval=1,  # Каждый 1 день
			# backupCount=7,  # Сохранять последние 7 файлов
			encoding="utf-8"  # Кодировка файла
		)
	]
)

# Создание нашего логгера
my_logger = log.getLogger('my_script_logger')
my_logger.setLevel(log.INFO)

# Запись сообщений в лог
# my_logger.debug("Отладочная информация")
# my_logger.info("Информационное сообщение")
# my_logger.warning("Предупреждение")
# my_logger.error("Ошибка")
# my_logger.critical("Критическая ошибка")
