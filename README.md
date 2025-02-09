## Зависимости
Для успешного запуска проекта необходимо установить следующие зависимости 
```sh
pip install python-telegram-bot
pip install opencv-python
pip install opencv-contrib-python
pip install pyzbar
pip install pytz
pip install mysql-connector-python
pip install numpy
pip install PyPDF2

apt-get install libzbar0
```
и настроить базу данных

## База данных
### Установка mysql-сервера и зависимостей
Для разворачивания локальной базы данных необходимо сделать следующее:
1. установить зависимости
```sh
pip install mysql-connector-python
sudo apt install mysql-server
```
после установки mysql сервер запустится автоматически

### Создание базы
1. Запуск mysql (требуется если сервис еще не запущен)
```sh
sudo mkdir /var/log/mysql && sudo chmod a+rw /var/log/mysql # команда для создания логов (обычно создаются автоматом при установке mysql)
sudo systemctl restart mysql # перезапуск сервиса

sudo mysql 	# запуск консоли mysql
```
2. Создание новой базы 'registry_birds' из скрипта
Запустить скрипт sql/create_with_data.sql командой
```sh
cat sql/create_with_data.sql | mysql -u newuser -p
```
3. Проверить наличие базы командой
```sql
SHOW DATABASES;     # список баз
USE registry_birds; 
SHOW TABLES;		# список таблиц в базе
```
### Создание пользователя
1. Создать нового пользователя с доступом к базе 'registry_birds'
```sql
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON registry_birds.* TO 'newuser'@'localhost';
SELECT user FROM mysql.user;  # вывод списка пользователей
```
2. Авторизация пользователя в базе
```sh
mysql -h localhost -u newuser -p
```

## Структура проекта
- main.py - точка входа в приложение
- взаимодействие с пользователем происходит в модуле ui. Точка входа это подмодуль ui.entry, он взаимодействует со всеми apm. Подмодули ui.apmX имеют две API-функции: 
```python
def apmX_start(username, text, key=None):
		return msg, keyboard, key
def apmX_entry(username, msg, key):
		return text, keyboard
```
- Функция apmX_start() вызывается, когда был введен текст. Аргументы: username - ник в тг, text - введенный текст, key - ключ, при первом вызове равен None, потом равен возвращаемому значению. Возвращает msg - текст выводимого сообщения, keyboard - набор кнопок в формате {'name1':'apmX_name1', 'name2':'apmX_name2'} где nameX это выводимые названия кнопок, apmX_nameY это ключи для функции apmX_entry()
- Функция apmX_entry() вызывается, когда была нажата кнопка. Аргументы: username - ник в тг, text - текст сообщения которое было выведено, key - ключ кнопки. Возвращает text - текст сообщения, если None, возврат в главное меню. keyboard - набор кнопок, если None, кнопки не отобразятся