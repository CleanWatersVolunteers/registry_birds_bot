# Установка необходимых инструментов на сервере
*Настройка осуществляется на Ubuntu server 24 и выше*

## доступ на сервер через ssh

```sh
# подключение
ssh username@server_ip_address

# прокидываем ключ для доступа по ключу а не по паролю
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
ssh-copy-id username@server_ip_address

```

## Ставим питон и окружение

0. Обновляем пакеты
```sh
sudo apt update
sudo apt upgrade
cd ~ # переходим в домашнюю директорию при необходимости
```
Если этого не сделать, при дальнейшей настройке могут быть проблемы

1. проверяем что установлен питон
```sh
python --version
```
Версия должна быть 3.12+. Если не установлен, ставим командой
```sh
sudo apt install python3
```

2. Разворачиваем виртуальное окружение
```sh
sudo apt install python3.12-venv
python3 -m venv venv
```
после этого используем python и pip:
venv/bin/python
venv/bin/pip

## Проверяем GIT

Ставим git если не установлен
```sh
sudo apt install git
```

## Устанавливаем супервизор(опционально, нужен для удаленного запуска бота)

```sh
sudo apt install supervisor
```
После установки проверяем что в файле /etc/supervisor/supervisord.conf есть строчки 
```
[include]
files = /etc/supervisor/conf.d/*.conf
```
если их нет, добавляем и запускаем командой
```sh
sudo supervisorctl start all
```
Команды супервизора
```sh
sudo supervisorctl reload  				# добавление нового сервиса из конфига 
sudo supervisorctl restart my_srv       # перезапуск сервиса my_srv
sudo supervisorctl start my_srv         # запуск сервиса my_srv
sudo supervisorctl stop my_srv          # остановка сервиса my_srv
sudo supervisorctl status               # список всех сервисов
```

## установка mysql

1. Устанавливаем командой
```sh
sudo apt install mysql-server  # после установки mysql сервер запустится автоматически
sudo service mysql status
```
после статуса проверяем что активно
```sh
mysql.service - MySQL Community Server
     Loaded: loaded (/usr/lib/systemd/system/mysql.service; enabled; preset: enabled)
     Active: active (running) since Fri 2025-03-07 22:20:27 MSK; 1min 0s ago
    Process: 2417 ExecStartPre=/usr/share/mysql/mysql-systemd-start pre (code=exited, status=0/SUCCESS)
   Main PID: 2450 (mysqld)
     Status: "Server is operational"
      Tasks: 37 (limit: 1090)
     Memory: 358.1M (peak: 387.8M)
        CPU: 2.103s
     CGroup: /system.slice/mysql.service
             └─2450 /usr/sbin/mysqld

```

2. Разворачивание базы
```sh
sudo mysql # запускаем SQL
mysql> CREATE DATABASE IF NOT EXISTS registry_birds; # создание базы
mysql> CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password'; # и создаем нового пользователя
mysql> GRANT ALL PRIVILEGES ON registry_birds.* TO 'newuser'@'localhost'; # разрешаем полный доступ к базе
mysql> SELECT user FROM mysql.user;  # вывод списка пользователей
mysql>exit; # выход
```

# Запуск и обновление бота

## Разворачивание бота на сервере
1. Качаем исходники
```sh
# создаем директорию для бота
mkdir registry_birds_bot
mkdir registry_birds_bot/production
mkdir registry_birds_bot/testing
cd registry_birds_bot/testing # для production дальнейшие действия повторяются

# качаем исходники с гита
git clone https://github.com/CleanWatersVolunteers/registry_birds_bot.git
cd registry_birds_bot
# проверяем ветку
git branch
# если не устраивает, переходим в новую ветку
git checkout new_branch
```
2. Разворачиваем базу
```sh
cat sql/create_with_data.sql | mysql -u newuser -p
```
3. Ставим зависимости питона
```sh
~/venv/bin/pip install -r requirements.txt
sudo apt-get install libzbar0
sudo apt-get install libgl1
```
4. Создаем файл .env с содержимым
```
TELEGRAM_BOT_TOKEN=
DB_NAME=registry_birds
DB_USER=user
DB_PASSWORD=pass
DB_HOST=localhost
DB_PORT=3306
```

## Настройка супервизора

1. Создать файл конфигурации в директории /etc/supervisor/conf.d с названием registry_birds_bot_testing.conf и следующим содержимым
```
[program:registry_birds_bot_testing]

user = root 

stdout_logfile = /var/log/registry_birds_bot_testing.out
stdout_logfile_maxbytes = 100MB
stderr_logfile = /var/log/registry_birds_bot_testing.err
stderr_logfile_maxbytes = 100MB

autorestart = true
startsecs = 5
startretries = 50
stopwaitsecs = 30

environment = PYTHONUNBUFFERED=1
directory = /root/registry_birds_bot/testing/registry_birds_bot               
command =  /root/venv/bin/python main.py
```
2. Обновить супервизор
```sh
sudo supervisorctl reload
sudo supervisorctl status # проверка успешности запуска
```
Все ошибки и логи смотреть командой
```sh
nano /var/log/registry_birds_bot_testing.err
nano /var/log/registry_birds_bot_testing.out
# Ctrl+End переход в конец файла
```

3. Для перезапуска бота использовать команду
```sh
sudo supervisorctl restart registry_birds_bot_testing
```
