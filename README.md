### Инструкция по сборке и запуску приложения

Для запуска данного веб приложения необходим `python3-flask`, который устанавливается с помощью команды

`sudo apt install python3-flask`

Чтобы скачать приложение необходимо склонировать репозиторий

`git clone https://github.com/Rosamon/secure_python_web.git && cd secure_python_web`


Далее необходимо использовать виртуальную среду

`python -m venv env && source ./env/bin/activate`

Скачать необходимые библиотеки из файла requirements.txt

`pip install -r requirements.txt`

Затем стоит запустить приложение через команду flask

`FLASK_APP=webapp.py FLASK_DEBUG=1 flask run`


### Комментарии к исправлениям
> Основные идеи исправлений для реализованных уязвимостей нужно описать в этом разделе.  
> Будет большим плюсом, если:
> - Исправления оформлены в виде отдельных коммитов
> - В этом разделе имеется рассуждение/обоснование надёжности внесённых исправлений

#### XSS - имплементировано в файле resources_xss.py



#### SQLi - имплементировано в файле resources_sqli.py

Строки 
```n=18
sqlite_connection = sqlite3.connect('./instance/app.db')
cursor = sqlite_connection.cursor()
cursor.execute("SELECT * FROM users WHERE username = '%s' AND secret = '%s'" % (username, secret))
record = cursor.fetchall()
cursor.close()
```
может быть заменена на
```
result = UserModel.query.filter_by(secret = secret).first()
```
Тем самым будет испоьзован проверенный и безопасный метод работы с БД через средства python, который, к тому же, более эффективный.

Однако, также можно эту часть кода преобразовать, добавив проверку и фильтрацию. Как и сделано в коде:
```n=18
sqlite_connection = sqlite3.connect('./instance/app.db')
cursor = sqlite_connection.cursor()
secret = re.escape(secret) # добавляем экранирование символов
if len(secret) > 120:
    secret=secret[0:119] # обрезаем строку, если она больше предпологаемой длины
cursor.execute("SELECT * FROM users WHERE username = '%s' AND secret = '%s'" % (username, secret))
record = cursor.fetchall()
cursor.close()
```

В данном случае хорошо работет экранирование, которое запрещает использовать символы, способные влиять на работу системы. А подмена символов на спец коды не привидет ни к какому результату.


#### IDOR - имплементировано в файле resources_idor.py




#### OS command injection - имплементировано в файле resources_osci.py



#### path traversal - имплементировано в файле resources_path.py


#### brute force - имплементировано в файле resources_bruteforce.py
