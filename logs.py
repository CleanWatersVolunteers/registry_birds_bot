import logging as log

log.basicConfig(
	level=log.INFO,
	format="%(asctime)s - %(levelname)s - %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S"
)

# Запись сообщений в лог
# log.debug("Отладочная информация")
# log.info("Информационное сообщение")
# log.warning("Предупреждение")
# log.error("Ошибка")
# log.critical("Критическая ошибка")
