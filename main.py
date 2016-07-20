# -*- coding: utf-8 -*-
import logging
from flask import Flask, render_template, request
from html2dat import perser

app = Flask(__name__, static_folder='static')

@app.route('/')
def top():
    """トップページを表示する"""
    return render_template('home.html')

@app.route('/api/dat', methods=['POST', 'GET'])
def todat():
    if request.method == 'POST':
        html = request.form['html'].encode('shift-jis')
        dat = perser.perse(html)
        if dat is None:
            return ''
        else:
            return unicode(dat, 'shift-jis', 'ignore')
    return ''

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
