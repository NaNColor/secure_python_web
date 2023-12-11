from flask import render_template, make_response, redirect, Flask, request, flash
from webapp import app
from models import UserModel
from flask_login import login_required, current_user
import sqlite3
import re

@app.route('/sqli', methods = ['POST', 'GET'])
@login_required
def index_sqli():
    if request.method == 'POST':
        username = current_user.username
        secret=request.form['secret']
        result = []
        if not secret:
            flash(f'Error: secret are required')
            return make_response(render_template('sqli.html',),200 )
        try:
            sqlite_connection = sqlite3.connect('./instance/app.db')
            cursor = sqlite_connection.cursor()
            secret = re.escape(secret)
            if len(secret) > 120:
                secret=secret[0:119]
            try:
                cursor.execute("SELECT * FROM users WHERE username = '%s' AND secret = '%s'" % (username, secret))
            except:
                flash(f'Error: you entered wrong secret')
                return make_response(render_template('sqli.html',), 200)
            record = cursor.fetchall()
            cursor.close()
            for x in record:
                result.append("Id: "+str(x[0])) 
                result.append("Username: "+x[1]) 
                result.append("Hash: "+x[2])
                result.append("Secret: "+x[3])
        except sqlite3.Error as error:
            flash(f'Error: can\'t connect to the bd')
            return make_response(render_template('sqli.html',),200 )
        finally:
            if (sqlite_connection):
                sqlite_connection.close()

        
        return make_response(render_template('sqli_2.html',information=result), 200)

    return make_response(render_template('sqli.html',), 200)