from flask import render_template, make_response, Flask, request, flash
from webapp import app
import subprocess


@app.route("/osci")
def index_osci():
    command = 'cat ' + request.args.get("filename")
    payload = ""
    if command:
        try:
            payload = subprocess.check_output(['cat', request.args.get("filename")], shell=False).decode("utf-8")
        except:
            flash(f'Do not change the URL!!!')
            payload = "Pleace, return to the main page and whisit this page again."
    return make_response(render_template('osci.html',payload = payload))