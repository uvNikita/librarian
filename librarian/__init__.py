# -*- coding: utf-8 -*-

from os import path

from flask import Flask

from .util import current_url
from .models import db
from .main.main import main

app = Flask(__name__)

app.config.from_object('config')
if not app.config.from_envvar('LIBRARIAN_SETTINGS', silent=True):
    app.config.from_pyfile('/etc/librarian.cfg', silent=True)
    app.config.from_pyfile(path.expanduser('~/.librarian.cfg'), silent=True)

app.register_blueprint(main)
db.init_app(app)
app.jinja_env.globals['current_url'] = current_url
