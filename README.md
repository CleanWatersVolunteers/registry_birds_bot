## Структура проекта
- main.py - точка входа в приложение
- botmenu.py - меню бота и основной функционал
- storage.py - модуль базы данных
- tgm.py - тут содержится функционал по формированию набора кнопок в формате тг апи
- logs.py - модуль для сохранения логов в файл, если функционал не нужен,внутри модуля можно отключить сохранение

## База данных
Для разворачивания локальной базы данных необходимо сделать следующее:
1. установить зависимости
```sh
pip install mysql-connector-python
sudo apt install mysql-server
```
после установки mysql сервер запустится автоматически

2. настроить доступ к SQL-базе
```sh
sudo mysql 	# запуск консоли
```
и в появившейся SQL-консоли добавить пользователя к базе 'registry_birds'
```sql
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON registry_birds.* TO 'newuser'@'localhost';
```
Проверка доступа к базе из консоли
```sh
mysql -h you_sql_server -u user_name -p
```
h — хост c MySQL. Если подключаемся с локальной машины, параметр можно опустить
u — имя пользователя MySQL (root или другой пользователь MySQL)
p — пароль, который будет предложено ввести после нажатия enter

3. Для работы с базой, ее необходимо создать. Для этого нужно запустить скрипт sql/create_with_data.sql командой
```sh
sudo mysql -u user -p < sql/create_with_data.sql
```