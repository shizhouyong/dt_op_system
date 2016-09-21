# -*- coding: utf-8 -*-

from flask import Blueprint, session, abort, render_template, request, flash, redirect, url_for

from server_operation import *
from utils.config import *
from utils.dbHelper import DbHelper

system = Blueprint('system', __name__)


# 主页
@system.route('/')
def default():
    if session.get('logged_in'):
        return redirect(url_for('system.index'))
    else:
        return redirect(url_for('system.login'))


@system.route('/index')
def index():
    return render_template("index.html")


# 修改密码
@system.route("/modify_password", methods=['POST'])
def modify_password():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("SELECT * FROM users WHERE username='" + request.form['username'] + "'")
    user = cur.fetchone()
    if user['password'] != request.form['old_pass']:
        return redirect(url_for('user.my_account', error='原密码错误,请重试'))
    else:
        g.db.execute("UPDATE users set password = '" + request.form['new_pass'] + "' WHERE username='" +
                     request.form['username'] + "'")
        g.db.commit()
        return redirect(url_for('system.login'))


# 我的账户
@system.route("/my_account/<error>")
def my_account(error):
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("select * from users")
    users = cur.fetchall()
    return render_template("my_account.html",
                           service_type=SERVICE_TYPE["SYSTEM_MANAGE"],
                           service_name=SYSTEM_MANAGE["MY_ACCOUNT"],
                           users=users,
                           error=error)


# 用户管理
@system.route("/account_manage")
def account_manage(error=None):
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    cur = g.db.execute("select * from users")
    users = cur.fetchall()
    cur2 = g.db.execute("select * from role")
    roles = cur2.fetchall()
    return render_template("users_manage.html",
                           service_type=SERVICE_TYPE["SYSTEM_MANAGE"],
                           service_name=SYSTEM_MANAGE["ACCOUNT_MANAGE"],
                           users=users,
                           roles=roles,
                           error=error)


# 新建用户
@system.route("/new_user", methods=['POST'])
def new_user():
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    role_id = DbHelper.get_role_id_by_remark(request.form['system_role'])
    print(role_id[0])
    g.db.execute('INSERT INTO users (email, username, password, system_role, position) VALUES (?, ?, ?, ?, ?)',
                 [request.form['email'],
                  request.form['username'],
                  request.form['password'],
                  role_id[0],
                  request.form['position']
                  ])
    g.db.commit()
    return redirect(url_for('system.account_manage'))


# 删除用户
@system.route("/delete_user/<user_id>")
def delete_user(user_id):
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    g.db.execute("DELETE FROM users WHERE id=" + user_id)
    g.db.commit()
    return redirect(url_for('system.account_manage'))


# 登录
@system.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html", error=None)
    else:
        cur = g.db.execute("SELECT * FROM users WHERE email='" + request.form['email'] + "' AND password='" +
                           request.form['password'] + "'")
        user = cur.fetchone()
        if not user:
            error = '邮箱或密码错误!'
        else:
            session['logged_in'] = True
            session['id'] = user[0]
            session['email'] = user[1]
            session['username'] = user[2]
            session['position'] = user[5]
            session['access'] = user[4]
            return redirect(url_for('system.index'))
        return render_template('login.html', error=error)


# 登出
@system.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('system.login'))


# 迭代周期管理
@system.route("/cycle_manage")
def cycle_manage():
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    cur = g.db.execute("select * from cycles")
    cycles = cur.fetchall()
    return render_template("cycles_manage.html",
                           service_type=SERVICE_TYPE["SYSTEM_MANAGE"],
                           service_name=SYSTEM_MANAGE["CYCLE_MANAGE"],
                           cycles=cycles)


# 新建迭代周期
@system.route("/new_cycle", methods=['POST'])
def new_cycle():
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    end = request.form['end']
    cycle_id = request.form['start'] + end[4:8]
    print(cycle_id)
    g.db.execute('insert into cycles(id,start,end,description) VALUES (?, ?, ?, ?)',
                 [cycle_id,
                  request.form['start'],
                  request.form['end'],
                  request.form['description']
                  ])
    g.db.commit()
    return redirect(url_for('system.cycle_manage'))


# 删除迭代周期
@system.route("/delete_cycle/<cycle_id>")
def delete_cycle(cycle_id):
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    g.db.execute("DELETE FROM cycles WHERE id=" + cycle_id)
    g.db.commit()
    return redirect(url_for('system.cycle_manage'))


# 删除迭代周期
@system.route("/stop_cycle/<cycle_id>")
def stop_cycle(cycle_id):
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    g.db.execute("UPDATE cycles SET status = 0 WHERE id=" + cycle_id)
    g.db.commit()
    return redirect(url_for('system.cycle_manage'))
