from markupsafe import escape
from flask import render_template, make_response, redirect, Flask, request, flash
from webapp import app
from models import UserModel
from flask_login import login_required, current_user


@app.route("/idor")
@login_required
def redirect_to_page():
    found_id = current_user.id
    # находим в бд пользователя текущей сессии и переходим на страницу с его id
    return redirect('/idor/'+str(found_id))

@app.route("/idor/<id>")
@login_required
def index_idor(id):
    
    current_id = escape(id)
    if int(current_user.id) != int(current_id):
        flash(f'You have not access to these data!')
        return redirect('/idor/'+str(current_user.id))

    user = UserModel.find_by_id(escape(current_id))

    return make_response(render_template('idor.html', secret=user.secret, username = user.username), 200)