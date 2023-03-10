# Скрипты для подключения к подпольному чату

Баба Зина ведёт двойную жизнь. Днём она печёт пирожки, гуляет с внуками и вяжет на спицах, а ночью – виртуозно строит в Майнкрафт фермы и курятники. Детство в деревне – это вам не кусь кошачий.  

На днях по Майнкрафт-сообществу прошла радостная новость: несколько умельцев создали чат для обмена кодами. Анонимный, история сообщений не сохраняется, войти и выйти можно в любой момент. Идеальное место для читеров.  

Репозиторий содержит два скрипта:  
 - `listen_minechat` - для прослушивания чата и сохранения истории переписки в файл
 - `send_minechat` - для регистрации нового пользователя и отправки сообщений в чат. 

## Как запустить

Для запуска потребуется Python версии не ниже 3.6  
### Прослушивание чата:

```bash
python listen_minechat.py
```
Обязательные аргументы, должны присутствовать либо в командной строке (имеют приоритет), либо в файле настроек `listen_minechat.ini`:
-  `-h` или `--host`   
  Указывается адрес или доменное имя сервера с чатом

-  `-p` или `port`  
Порт для подключения к чату на прослушку  

Необязательные аргументы:  
- `--history`  
  Задается имя файла, в который сохраняется переписка в чате. По умолчанию `history.txt`  
  
Файл настроек `listen_minechat.ini`
```ini
host = minechat.secret_lair.org
port = 5050
history = chat2.txt
```
### Отправка сообщений в чат
```bash
python send_minechat.py -h HOST -p PORT [-t TOKEN | -u USER] message
```
Обязательные аргументы, должны присутствовать либо в командной строке (имеют приоритет), либо в файле настроек `send_minechat.ini`:
- `message`  
текст сообщения, которое будет отправлено в чат.  
-  `-h` или `--host`   
Указывается адрес или доменное имя сервера с чатом

-  `-p` или `port`   
Порт для подключения к чату на отправку сообщений  

Необязательные аргументы:

 - `-t` или `--token`    
Токен для авторизации в чате  

 - `-u` или `user`  
Имя нового пользователя для регистрации в чате. Будет зарегистрирован новый пользователь, полученный токен доступа будет сохранен в файл `.token`. Существующий токен будет перезаписан. В командной сроке может быть указано либо имя пользователя, либо токен доступа. Если ни токен доступа, ни имя пользователя не указано, то скрипт сначала попытается использовать токен из файла `.token`, а при его отсутствии произведет регистрацию нового пользователя, для чего запросит его имя.

Формат файла `send_minechat.ini` аналогичен файлу `listen_minechat.ini`
# Цели проекта  
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
