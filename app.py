# -*- coding: utf-8 -*-

import os
import sqlite3
import time

from flask import Flask, g, render_template, session, flash, url_for, request, redirect, abort, Blueprint

from server_operation import *

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

SERVICE_TYPE = {"MAIN_SERVICE": "运维服务", "USER_CENTER": "个人中心", "ACCESS_CENTER": "权限中心"}
MAIN_SERVICE = {"BUILD": "war包构建", "WAR_MANAGE": "war包管理", "SERVER_MANAGE": "服务器管理", "CONTAINER_MANAGE": "容器管理",
                "TOMCAT_MANAGE": "Tomcat管理", "PROJECT_MANEGE": "工程管理", "DEPLOY_MANEGE": "部署管理"}
USER_CENTER = {"MY_ACCOUNT": "我的账号", "ACCOUNT_MANAGE": "账号管理", "ACCESS_MANAGE": "权限管理"}
ENVIRONMENT = {"MASTER": "vomoho_master", "DEVELOP": "vomoho_develop", "LOCAL_DEVELOP": "local_develop"}
DEPLOY_ITEM = {"NEW_DEPLOY": "新建部署", "ALL_DEPLOY": "所有部署", "PROJECT_DEPLOY": "工程部署", "REVIEW_DEPLOY": "部署审核",
               "DETAILS_DEPLOY": "部署详情"}


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


@app.teardown_request
def teardown_request(exception):
    if exception is not None:
        print(exception)
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()


# 主页,默认到war包构建
@app.route('/')
def default():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/index')
def index():
    return render_template("index.html")


# war包构建页面/提交构建请求
@app.route('/war_build/<environment>/<int:page>', methods=['GET'])
@app.route('/war_build/<environment>', methods=['GET'])
@app.route('/war_build', methods=['POST'])
def war_build(environment='local_develop', page=1):
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        cur = g.db.execute("SELECT * FROM builds_record WHERE environment='" + environment + "' ORDER BY id DESC")
        builds = cur.fetchall()
        cur2 = g.db.execute("SELECT * FROM tomcats ORDER BY id DESC")
        tomcats = cur2.fetchall()
        return render_template("war_build.html",
                               service_type=SERVICE_TYPE["MAIN_SERVICE"],
                               service_name=MAIN_SERVICE["BUILD"],
                               environment=environment,
                               page=page,
                               builds=builds,
                               tomcats=tomcats)
    else:
        if not session.get('logged_in'):
            abort(401)

    g.db.execute("INSERT INTO builds_record (time, build_desc, operator, process, environment,tomcat) VALUES (?, ?, ?, ?, ?, ?)",
                 [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  request.form['build_desc'],
                  session.get('username'),
                  '构建请求已发出',
                  request.form['branch'],
                  request.form['tomcat']])
    g.db.commit()
    if request.form['branch'] == ENVIRONMENT["MASTER"]:
        os.system('curl %s/job/vomoho_master/build?delay=0sec' % cf.get("jenkins", "url"))
        pass
    elif request.form['branch'] == ENVIRONMENT["DEVELOP"]:
        os.system('curl %s/job/vomoho_develop/build?delay=0sec' % cf.get("jenkins", "url"))
        pass
    else:
        os.system('curl %s/job/local_develop/build?delay=0sec' % cf.get("jenkins", "url"))
    return redirect(url_for('war_build', environment=request.form['branch'], _method='GET'))


# Jenkins开始构建/完成接口
@app.route('/war_build/update/<branch>/<operation>/<war_name>')
def build_master_start(branch='develop', operation='start', war_name=''):
    cur = g.db.execute("SELECT * FROM builds_record WHERE environment='" + branch + "' ORDER BY id DESC LIMIT 0,1")
    last_build = cur.fetchone()
    if operation == 'finish' and last_build[7] != 0 and last_build[4] == 'Jenkins已开始构建':
        publish_tomcat(branch, war_name, last_build[7])

    if operation == 'start':
        if last_build[4] != '构建完毕' and last_build[4] != '发布完毕':
            g.db.execute("UPDATE builds_record SET process = 'Jenkins已开始构建' WHERE id = " + str(last_build[0]))
    elif operation == 'finish':
        g.db.execute("UPDATE builds_record SET process = '构建完毕', war_name = '" + war_name + "' WHERE id = " + str(last_build[0]))
    elif operation == 'published':
        g.db.execute("UPDATE builds_record SET process = '发布完毕' WHERE id = " + str(last_build[0]))
    g.db.commit()
    return "success"


# 新建实例
@app.route('/server_new', methods=['POST'])
def server_new():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO servers (aliid, name, ip_outer, ip_inner, environment) VALUES (?, ?, ?, ?, ?)',
                 [request.form['aliid'],
                  request.form['name'],
                  request.form['ip_outer'],
                  request.form['ip_inner'],
                  request.form['environment']])
    g.db.commit()
    return redirect(url_for('server_manage'))


# 工程列表
@app.route("/project_list")
def project_list():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("select p.*, u.username from projects p, user u where p.manager = u.id")
    projects = cur.fetchall()
    cur2 = g.db.execute("select * from user")
    users = cur2.fetchall()
    return render_template("project_list.html",
                           service_type=SERVICE_TYPE["MAIN_SERVICE"],
                           service_name=MAIN_SERVICE["PROJECT_MANEGE"],
                           projects=projects,
                           users=users)


# 新建工程
@app.route("/new_project", methods=['POST'])
def new_project():
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    cur = g.db.execute('select id from projects ORDER BY pid DESC')
    num = cur.fetchone()

    g.db.execute('INSERT INTO projects (pid,name,jenkins_name,manager,description) VALUES (?, ?, ?, ?, ?)',
                 [num[0]+1001,
                  request.form['project_name'],
                  request.form['jenkins_name'],
                  request.form['manager'][0],
                  request.form['description']])
    g.db.commit()
    return redirect(url_for('project_list'))


# 删除工程
@app.route("/delete_project/<project_id>")
def delete_project(project_id):
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    g.db.execute("DELETE FROM projects WHERE pid=" + project_id)
    g.db.commit()
    return redirect(url_for('project_list'))


# 更新工程
@app.route("/update_project", methods=['POST'])
def update_project():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('UPDATE projects set name = ?,jenkins_name = ?,manager = ?,description = ? where pid = ?',
                 [request.form['project_name'],
                  request.form['jenkins_name'],
                  request.form['manager'][0],
                  request.form['description'],
                  request.form['project_pid']])
    g.db.commit()
    return redirect(url_for('project_list'))


# 部署管理/新建部署/审核部署/查看部署列表
@app.route('/deploy_manage/<item>/<int:page>', methods=['GET'])
@app.route('/deploy_manage/<item>', methods=['GET'])
@app.route('/deploy_manage', methods=['POST'])
def deploy_manage(item, page=1):
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        if item == 'REVIEW_DEPLOY':
            cur = g.db.execute(
                "with a as(select d.*,u.username submitter_name from deploys d,user u "
                "where d.submitter_id = u.id),"
                "b as(select a.*,u.username reviewer_name from a,user u where a.reviewer_id=u.id),"
                "c as (select b.*,u.username tester_name from b,user u where b.testers_id=u.id)"
                "select c.id id,c.time time,c.status status,c.description description,"
                "c.submitter_name submitter_name,c.reviewer_name reviewer_name,c.tester_name "
                "tester_name,p.name project_name from c,projects p where c.project_id = p.pid and c.reviewer_name = '"
                + session.get("username") + "'")
            deploys = cur.fetchall()
            return render_template("deploy_list.html",
                                   service_type=SERVICE_TYPE["MAIN_SERVICE"],
                                   service_name=MAIN_SERVICE["DEPLOY_MANEGE"],
                                   deploy_item=DEPLOY_ITEM[item],
                                   item=item,
                                   page=page,
                                   deploys=deploys)
        elif item == 'ALL_DEPLOY':
            cur = g.db.execute(
                "with a as(select d.*,u.username submitter_name from deploys d,user u "
                "where d.submitter_id = u.id),"
                "b as(select a.*,u.username reviewer_name from a,user u where a.reviewer_id=u.id),"
                "c as (select b.*,u.username tester_name from b,user u where b.testers_id=u.id)"
                "select c.id id,c.time time,c.status status,c.description description,"
                "c.submitter_name submitter_name,c.reviewer_name reviewer_name,c.tester_name "
                "tester_name,p.name project_name from c,projects p where c.project_id = p.pid")
            deploys = cur.fetchall()
            return render_template("deploy_list.html",
                                   service_type=SERVICE_TYPE["MAIN_SERVICE"],
                                   service_name=MAIN_SERVICE["DEPLOY_MANEGE"],
                                   deploy_item=DEPLOY_ITEM[item],
                                   item=item,
                                   page=page,
                                   deploys=deploys)

    else:
        if not session.get('logged_in'):
            abort(401)


# 部署审核/查看详情/批准/拒绝
@app.route('/deploy_review/<item>/<int:did>', methods=['GET'])
@app.route('/deploy_review/<item>', methods=['GET'])
@app.route('/deploy_review', methods=['POST'])
def deploy_review(item, did):
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("select project_id from deploys where id = " + str(did))
    project_id = cur.fetchone()
    if request.method == 'GET':
        if item == 'DETAILS_DEPLOY':
            cur = g.db.execute(
                "with a as(select d.*,u.username submitter_name from deploys d,user u "
                "where d.submitter_id = u.id and d.id = " + str(did) + "),"
                "b as(select a.*,u.username reviewer_name from a,user u where a.reviewer_id=u.id),"
                "c as (select b.*,u.username tester_name from b,user u where b.testers_id=u.id)"
                "select c.id id,c.time time,c.status status,c.description description,"
                "c.submitter_name submitter_name,c.reviewer_name reviewer_name,c.tester_name "
                "tester_name,p.name project_name from c,projects p where c.project_id = p.pid")
            deploy = cur.fetchone()
            return render_template("deploy_details.html",
                                   service_type=SERVICE_TYPE["MAIN_SERVICE"],
                                   service_name=MAIN_SERVICE["DEPLOY_MANEGE"],
                                   deploy_item=DEPLOY_ITEM[item],
                                   item=item,
                                   deploy=deploy)
        elif item == 'APPROVAL_DEPLOY':
            g.db.execute("update deploys set status = 2 where id = " + str(did))
            g.db.commit()
            return redirect(url_for("submit_deploy", project_id=project_id[0]))
        elif item == 'REFUSE_DEPLOY':
            g.db.execute("update deploys set status = 3 where id = "+ str(did))
            g.db.commit()
            return redirect(url_for("submit_deploy", project_id=project_id[0]))
    else:
        if not session.get('logged_in'):
            abort(401)


# 新建部署
@app.route("/new_deploy", methods=['POST'])
def new_deploy():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute('select id from user where username = ?', [session.get('username')])
    num = cur.fetchone()
    print(num[0])
    g.db.execute('INSERT INTO deploys(submitter_id,reviewer_id,project_id,description) '
                 'values (?, ?, ?, ?)',
                 [num[0],
                  request.form['reviewer'][0],
                  request.form['project_id'],
                  request.form['deploy_desc']])
    g.db.commit()
    return redirect(url_for('submit_deploy', project_id=request.form['project_id']))


# 删除部署
@app.route("/delete_deploy/<deploy_id>")
def delete_deploy(deploy_id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("DELETE FROM deploys WHERE id=" + deploy_id)
    g.db.commit()
    return redirect(url_for('deploy_manage'))


# 服务器管理
@app.route("/server_manage")
def server_manage():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("SELECT * FROM servers ORDER BY environment DESC")
    servers = cur.fetchall()
    return render_template("server_manage.html",
                           service_type=SERVICE_TYPE["MAIN_SERVICE"],
                           service_name=MAIN_SERVICE["SERVER_MANAGE"],
                           servers=servers)


# tomcat管理
@app.route("/tomcat_manage")
def tomcat_manage():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("SELECT id, aliid, name, ip_outer, ip_inner, path, port  FROM tomcats ORDER BY id DESC")
    tomcats = cur.fetchall()
    return render_template("tomcat_manage.html",
                           service_type=SERVICE_TYPE["MAIN_SERVICE"],
                           service_name=MAIN_SERVICE["TOMCAT_MANAGE"],
                           tomcats=tomcats)


# 新建tomcat实例
@app.route('/tomcat_new', methods=['POST'])
def tomcat_new():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO tomcats (aliid, name, ip_outer, ip_inner, path, port, username, password) '
                 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 [request.form['aliid'],
                  request.form['name'],
                  request.form['ip_outer'],
                  request.form['ip_inner'],
                  request.form['path'],
                  request.form['port'],
                  request.form['ServerUsername'],
                  request.form['ServerPassword']])
    g.db.commit()
    return redirect(url_for('tomcat_manage'))


# 删除实例
@app.route('/tomcat_delete/<tomcat_id>')
def tomcat_delete(tomcat_id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("DELETE FROM tomcats WHERE id=" + tomcat_id)
    g.db.commit()
    return redirect(url_for('tomcat_manage'))


# 删除实例
@app.route('/server_delete/<server_id>')
def server_delete(server_id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("DELETE FROM servers WHERE id=" + server_id)
    g.db.commit()
    return redirect(url_for('server_manage'))


# war包管理
@app.route("/war_manage/<environment>", methods=['GET'])
@app.route('/war_manage/<environment>/<int:page>', methods=['GET'])
def war_manage(environment='local_develop', page=1):
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        sources = srv_get_fetcher_containers(environment)
        wars = srv_getwars(environment)
        return render_template('war_manage.html',
                               service_type=SERVICE_TYPE["MAIN_SERVICE"],
                               service_name=MAIN_SERVICE["WAR_MANAGE"],
                               page=page,
                               environment=environment,
                               wars=wars,
                               sources=sources)


# 删除war包
@app.route('/war_manage/war_delete/<environment>/<war_name>', methods=['GET'])
def war_delete(war_name, environment='local_develop'):
    if not session.get('logged_in'):
        abort(401)
    srv_war_delete(environment, war_name)
    return redirect(url_for('war_manage', environment=environment))


# 新建代码源
@app.route('/war_manage/new_source', methods=['POST'])
def new_source():
    if not session.get('logged_in'):
        abort(401)
    srv_new_source(request.form['environment'], request.form['source_name'], request.form['war'])
    return redirect(url_for('war_manage', environment=request.form['environment']))


# 删除代码源
@app.route('/war_manage/delete_source/<source_name>/<environment>')
def delete_source(source_name, environment='local_develop'):
    if not session.get('logged_in'):
        abort(401)
    srv_stop_and_delete_container(source_name)
    return redirect(url_for('war_manage', environment=environment))


# 容器管理
@app.route("/container_manage/<environment>", methods=['GET'])
def container_manage(environment='local_develop'):
    if not session.get('logged_in'):
        abort(401)
    sources = srv_get_fetcher_containers(environment)
    containers = srv_get_tomcat_containers(environment)
    return render_template("container_manage.html",
                           service_type=SERVICE_TYPE["MAIN_SERVICE"],
                           service_name=MAIN_SERVICE["CONTAINER_MANAGE"],
                           environment=environment,
                           containers=containers,
                           sources=sources)


# 新建容器
@app.route("/container_manage/new_container", methods=['POST'])
def new_container():
    if not session.get('logged_in'):
        abort(401)
    srv_new_container(request.form['source_name'], request.form['container_name'])
    return redirect(url_for('container_manage', environment=request.form['environment']))


# 停止并删除容器
@app.route("/container_manage/<environment>/delete/<container_id>", methods=['GET'])
def stop_and_delete_container(container_id, environment='local_develop'):
    if not session.get('logged_in'):
        abort(401)
    srv_stop_and_delete_container(container_id)
    return redirect(url_for('container_manage', environment=environment))


# 我的账户
@app.route("/my_account")
def my_account(error=None):
    return render_template("my_account.html",
                           service_type=SERVICE_TYPE["USER_CENTER"],
                           service_name=USER_CENTER["MY_ACCOUNT"],
                           error=error)


# 修改密码
@app.route("/my_account/modify_password", methods=['POST'])
def modify_password():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("SELECT * FROM user WHERE username='" + request.form['username'] + "'")
    user = cur.fetchone()
    if user.get('password') != request.form['password']:
        return redirect(url_for('my_account', error='原密码错误,请重试'))


# 用户管理
@app.route("/account_manage")
def account_manage():
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    cur = g.db.execute("select * from user")
    users = cur.fetchall()
    return render_template("users_manage.html",
                           service_type=SERVICE_TYPE["USER_CENTER"],
                           service_name=USER_CENTER["ACCOUNT_MANAGE"],
                           users=users)


# 新建用户
@app.route("/new_user", methods=['POST'])
def new_user():
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    g.db.execute('INSERT INTO user (email, username, position, password, role_id) VALUES (?, ?, ?, ?, ?)',
                 [request.form['email'],
                  request.form['username'],
                  request.form['position'],
                  request.form['password'],
                  request.form['role'][0]])
    g.db.commit()
    return redirect(url_for('account_manage'))


# 删除用户
@app.route("/delete_user/<user_id>")
def delete_user(user_id):
    if (not session.get('logged_in')) or (session.get('username') != 'admin'):
        abort(401)
    g.db.execute("DELETE FROM user WHERE id=" + user_id)
    g.db.commit()
    return redirect(url_for('account_manage'))


# 登录
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html", error=None)
    else:
        cur = g.db.execute("SELECT * FROM user WHERE email='" + request.form['email'] + "' AND password='" +
                           request.form['password'] + "'")
        users = cur.fetchone()
        if not users:
            error = '邮箱或密码错误!'
        else:
            session['logged_in'] = True
            session['email'] = users[1]
            session['username'] = users[2]
            session['position'] = users[4]
            return redirect(url_for('index'))
        return render_template('login.html', error=error)


# 登出
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)







