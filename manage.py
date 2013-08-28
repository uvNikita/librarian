# -*- coding: utf-8 -*-

from flask.ext.script import Manager

from librarian import app
from librarian.models import db

manager = Manager(app)


@manager.command
def init_db():
    """ Initialize database: drop and create all columns """
    db.drop_all()
    db.create_all()


if __name__ == "__main__":
    manager.run()
