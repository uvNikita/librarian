# -*- coding: utf-8 -*-

from os import path

from flask import Flask

from librarian.util import current_url
from librarian.models import db
from librarian.blueprints import librarian

app = Flask(__name__)

app.config.from_object('config')
if not app.config.from_envvar('LIBRARIAN_SETTINGS', silent=True):
    app.config.from_pyfile('/etc/librarian.cfg', silent=True)
    app.config.from_pyfile(path.expanduser('~/.librarian.cfg'), silent=True)

app.register_blueprint(librarian)
db.init_app(app)
app.jinja_env.globals['current_url'] = current_url
