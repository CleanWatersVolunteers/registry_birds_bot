## Структура проекта
- main.py - точка входа в приложение
- ui_*.py - файлы меню для взаимодействия с пользователем
- storage.py - модуль базы данных
- logs.py - модуль для сохранения логов в файл, если функционал не нужен,внутри модуля можно отключить сохранение
- в корне проекта должен лежать файл token с токеном бота, а также config.json с данными для работы с базой данных(установка см. далее)

### Зависимости
Необходимо установить следующие зависимости 
```sh
pip install requirements.txt
apt-get install libzbar0
```
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
cat sql/create_with_data.sql | mysql
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