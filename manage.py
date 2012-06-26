# -*- coding: utf-8 -*-

from flaskext.script import Manager

from librarian import app

manager = Manager(app)

if __name__ == "__main__":
    manager.run()
