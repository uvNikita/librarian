# -*- coding: utf-8 -*-

from flask import Flask

from librarian.blueprints import librarian
from librarian.models import db

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://librarian:librarian_pass@192.168.138.100/library'
app.register_blueprint(librarian)
db.init_app(app)
