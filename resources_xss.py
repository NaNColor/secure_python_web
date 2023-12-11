from flask import render_template, make_response, redirect, Flask, request, flash
from webapp import app
from models import CommentsModel

def escape_XSS(string):
    string = string.replace('&','&amp')
    string = string.replace('<','&lt')
    string = string.replace('>','&gt')
    string = string.replace('"','&quot')
    string = string.replace('\'','&#x27')
    return string

@app.route('/xss', methods = ['POST', 'GET'])
def index_xss():
    if request.method == 'POST':
        text=request.form['text']
        text=escape_XSS(text)
        if not text:
            flash(f'Error: Can\'t sent these comment {text}')
        else:
            NewComment = CommentsModel(text = text)
            NewComment.save_to_db()
    comments = CommentsModel.getAll()
    if not comments:
        comments = "Be first!!!"
    ref = make_response(render_template('xss.html', comments=comments), 200)
    return ref
