# -*- coding: utf-8 -*-

from flask import Flask, g
import os
import sqlite3
from views.build import build
from views.project import project
from views.system import system
from views.deploy import deploy
import configparser

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
        DATABASE=os.path.join(app.root_path, 'opsys.db'),
        DEBUG=True,
        SECRET_KEY='development key',
        USERNAME='admin',
        PASSWORD='default'
))

app.config.from_envvar('OPSYS_SETTINGS', silent=True)

app.register_blueprint(system)  # 注册system蓝图
app.register_blueprint(project, url_prefix='/project')  # 注册project蓝图
app.register_blueprint(build, url_prefix='/build')  # 注册build蓝图
app.register_blueprint(deploy, url_prefix='/deploy')  # 注册api蓝图


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.before_request
def before_request():
    g.db = connect_db()
    g.cf = configparser.ConfigParser()
    g.cf.read("config.iml")


@app.teardown_request
def teardown_request(exception):
    if exception is not None:
        print(exception)
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # 运行flask http程序，host指定监听IP，port指定监听端口，调试时需要开启debug模式。


