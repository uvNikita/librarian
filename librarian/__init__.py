from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://librarian:librarian_pass@192.168.138.100/library'
db = SQLAlchemy(app)

import librarian.webui
