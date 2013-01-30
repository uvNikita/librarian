# -*- coding: utf-8 -*-

from flaskext.script import Manager

from librarian import app
from librarian.models import db

manager = Manager(app)


@manager.command
def init_db():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    manager.run()
