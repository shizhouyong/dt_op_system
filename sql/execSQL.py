# -*- coding: utf-8 -*-
import os
import sqlite3
from contextlib import closing

# create our little application :)
from flask import Flask

app = Flask(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
        DATABASE=os.path.join(app.root_path, '../opsys.db'),
        DEBUG=True,
))
app.config.from_envvar('OPSYS_SETTINGS', silent=True)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('init_builds.sql', mode='rb') as f:
            db.cursor().executescript(f.read().decode('utf8'))
        db.commit()


init_db()
