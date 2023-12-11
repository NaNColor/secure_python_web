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

Средства jinja2, которые использует flask, по умолчанию имеют средства предотвращения XSS. Но это не показательно.

В данном случае также можно использовать замену символов для html, например написав следующий скрипт:
```
def escape_XSS(string):
    string = string.replace('&','&amp')
    string = string.replace('<','&lt')
    string = string.replace('>','&gt')
    string = string.replace('"','&quot')
    string = string.replace('\'','&#x27')
    return string
```
Испоьлзуя эту функцию перед загрузкой комментария (`text=escape_XSS(text)`) мы избежим влияния самого комментария на тело html, тем самым превращая скрипт в простой текст. Не может влиять на поведение сайта = безопасно.

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

Лучший способ избежать подобную уязвимость в данном случае - строгий контроль сессии: если авторизованный пользователь не имеет ничего общего с данными, к которым пытается попасть, значит это не его данные. 
Для реализации этого достаточно добавить проврерку сессии во время доступа к данным.
Добавив строки ниже можно добится нужного результата.

```
current_id = escape(id)
if current_user.id != current_id:
    flash(f'You have not access to these data!')
```


#### OS command injection - имплементировано в файле resources_osci.py

По хорошему в коде не должно происходить взаимодействие с ОС на прямую по запросу пользователя: как минимум такой код заслуживает особого внимания и минимальные права, а любая возможность исполнения команд пользователя не должна существовать. Таким образом, лучше всего заменить команды исполнения, на те, которые выполняют только заданную функцию. Например `eval("cat file")`на `open(file, "r"); f.readline()`. Но можно попробовать обезопасить и команды исполнения кода.

В текущем коде это делается просто заменой `payload = subprocess.check_output(command, shell=True).decode("utf-8")` на `payload = subprocess.check_output(['cat', request.args.get("filename")], shell=False).decode("utf-8")`. Тем самым запрещается использование комманд оболочки, выходящие за рамки дозволенной одной команды "cat".


#### path traversal - имплементировано в файле resources_path.py

Здесь можно избежать этой уязвимости путем контроля ввода нелегетимных комбинаций символов по типу "../". Для этого я использовал следующую конструкцию в коде:
```
while "../" in filename or "/" in filename:
        filename = filename.replace("../","")
        filename = filename.replace("/","")
    payload = ""
    try:
        payload = open(filename, "r").read()
    except:
        flash(f'Somthing went wrong...')
```

Так как можно попробовать обойти одинарную замену символов, я решил сделать это циклически, чтобы избежать попытки перехитрить удаление "../". Я считаю, в данном случае этот код реализует защиту от path traversal. Лучший способ защиты в данном случае - проверять, соответсвует ли введенная строка файлам, которые могут быть отображены.

#### brute force - имплементировано в файле resources_bruteforce.py

Защита от брутфорса может быть различной: от обязательного ввода капчи, до блокирования адресов на основе конфигураций fail2ban.

Я решил добавить в свое приложение капчу. Для этого добавил в файл `webapp.py` строки конфигурации:

```
from flask_simple_captcha import CAPTCHA
YOUR_CONFIG = {
    'SECRET_CAPTCHA_KEY': '9e977ef74bf744ac153c118a2c9e76c9',
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': False,
    'EXPIRE_SECONDS': 600,
}
SIMPLE_CAPTCHA = CAPTCHA(config=YOUR_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)
```
А также добавил код в файл работы с запросами.
```
new_captcha_dict = SIMPLE_CAPTCHA.create()
c_hash = request.form.get('captcha-hash')
c_text = request.form.get('captcha-text')
if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
    flash(f'Error: Wrong captcha')
    return make_response(render_template('bruteforce.html',captcha=new_captcha_dict),200 )
```

Теперь чтобы войти пользователь должен ввести капчу, которая обновляется каждый раз, когда страница загружается.
Таким образом брутфорс атака с этой стороны сайта становится не рентабильной.

