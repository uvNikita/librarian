# -*- coding: utf-8 -*-

from flask import Flask

from librarian.util import current_url
from librarian.models import db
from librarian.blueprints import librarian

app = Flask(__name__)

app.config.from_object('config')

app.register_blueprint(librarian)
db.init_app(app)
app.jinja_env.globals['current_url'] = current_url
