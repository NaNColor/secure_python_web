from flask import Flask, render_template, make_response, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256 as sha256
from flask_login import LoginManager

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8e977ef74bf745ac153c117a2c9e76c6'

from flask_simple_captcha import CAPTCHA
YOUR_CONFIG = {
    'SECRET_CAPTCHA_KEY': '9e977ef74bf744ac153c118a2c9e76c9',
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': False,
    'EXPIRE_SECONDS': 600,
}
SIMPLE_CAPTCHA = CAPTCHA(config=YOUR_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)


db = SQLAlchemy(app)





with app.app_context():
    db.create_all()


@app.route('/')
def index():
    ref = make_response(render_template('index.html',),200)
    return ref

import models, resources_xss, resources_sqli, resources_idor, resources_osci, resources_path, resources_bruteforce
from models import UserModel
login_manager = LoginManager()
login_manager.login_view = '/bruteforce'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

@app.route('/registration', methods = ['POST', 'GET'])
def index_registration():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        secret = request.form['secret']
        if not password or not username or not secret:
            flash(f'Error: filelds are required')
            return make_response(render_template('registration.html',),200 )

        new_user = UserModel(
            username = username,
            password = UserModel.generate_hash(password),
            secret = secret
        )
        try:
            new_user.save_to_db()          
        except Exception as e:
            flash(f'Error: {e}')
            return make_response(render_template('registration.html',),200 )

        return make_response(render_template('bruteforce_2.html',), 200)

    return make_response(render_template('registration.html',), 200)

# xss - возможность для коменнтариев
# sqli - вывод информации о текущем пользователе
# idor - секрет пользователя по ID
# osci - через exec исполняем файл, который читает другой файл exec(open("./filename").read())
# path traversal - читаем файл из пути
# brute force - простая авторизация





#app.run(host='127.0.0.1', port=8000, debug=True)