# -*- coding: utf-8 -*-

import os
import time

from flask import Blueprint, session, abort, render_template, request, redirect, url_for, json, jsonify

from server_operation import *
from utils.config import *
from utils.dbHelper import DbHelper
build = Blueprint('build', __name__)


# 新建服务器
@build.route('/server_new', methods=['POST'])
def server_new():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO servers (aliid, name, type, username, password, ip_outer, ip_inner, environment) '
                 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 [request.form['aliid'],
                  request.form['name'],
                  request.form['server_type'],
                  request.form['username'],
                  request.form['password'],
                  request.form['ip_outer'],
                  request.form['ip_inner'],
                  request.form['environment']])
    g.db.commit()
    return redirect(url_for('build.server_manage'))


# 服务器管理
@build.route("/server_manage")
def server_manage():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("SELECT * FROM servers ORDER BY environment DESC")
    servers = cur.fetchall()
    return render_template("server_manage.html",
                           service_type=SERVICE_TYPE["PROJECT_MANEGE"],
                           service_name=PROJECT_MANEGE["SERVER_MANAGE"],
                           servers=servers)


# 删除实例
@build.route('/server_delete/<server_id>')
def server_delete(server_id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("DELETE FROM servers WHERE id=" + server_id)
    g.db.commit()
    return redirect(url_for('build.server_manage'))


# 删除实例
@build.route('/running_env_delete/<env_id>')
def running_env_delete(env_id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("DELETE FROM running_env WHERE id=" + env_id)
    g.db.commit()
    return redirect(url_for('build.server_manage'))


# 新建服务运行环境环境
@build.route('/server_environment_new', methods=['POST'])
def server_environment_new():
    if not session.get('logged_in'):
        abort(401)
    server_id = DbHelper.get_server_id_by_name(request.form['server'])
    g.db.execute('INSERT INTO running_env (name, server_id, file_path, pre_shell, pos_shell) VALUES (?, ?, ?, ?, ?)',
                 [request.form['name'],
                  server_id[0],
                  request.form['env_path'],
                  request.form['pre_shell'],
                  request.form['pos_shell']])
    g.db.commit()
    return redirect(url_for('build.server_manage'))


# 更新工程
@build.route("/update_running_env", methods=['POST'])
def update_running_env():
    if not session.get('logged_in'):
        abort(401)

    pid = request.form['hidden_server_env_pid']

    g.db.execute('UPDATE running_env set name = ?,pre_shell = ?,pos_shell = ?'
                 'where id = ?',
                 [request.form['env_name'],
                  request.form['pre_shell'],
                  request.form['pos_shell'],
                  pid])
    g.db.commit()
    return redirect(url_for('build.server_manage'))


# 服务器部署环境列表
@build.route('/get_env_list/<server_name>', methods=['GET'])
def get_env_list(server_name):
    if not session.get('logged_in'):
        abort(401)
    server_id = DbHelper.get_id_server_name(server_name)
    running_envs = DbHelper.get_env_by_server_id(server_id[0])
    envs = []
    for result in running_envs:
        env = {
            "id": result[0],
            "name": result[1],
            "server_id": result[2],
            "deploy_time": result[3],
            "file_path": result[4],
            "pre_shell": result[5],
            "pos_shell": result[6]
        }
        envs.append(env)
    response = {"result": envs}
    json_str = json.dumps(response)
    return jsonify(result=json_str)


# 服务器部署环境详情
@build.route('/get_env_info/<env_id>', methods=['GET'])
def get_env_info(env_id):
    if not session.get('logged_in'):
        abort(401)
    env_info = DbHelper.get_env_info_by_id(env_id)
    info = []
    print(env_info[1])

    env = {
        "id": env_info[0],
        "name": env_info[1],
        "server_id": env_info[2],
        "deploy_time": env_info[3],
        "file_path": env_info[4],
        "pre_shell": env_info[5],
        "pos_shell": env_info[6]
    }
    info.append(env)
    response = {"result": info}
    json_str = json.dumps(response)
    return jsonify(result=json_str)


# 服务器部署环境修改
@build.route('/preserve_env_info', methods=['POST'])
def preserve_env_info():
    if not session.get('logged_in'):
        abort(401)
    env_id = request.form['hidden_server_env_id']

    g.db.execute('UPDATE running_env set name = ?,file_path = ?, pre_shell = ?,pos_shell = ?'
                 'where id = ?',
                 [request.form['env_name'],
                  request.form['file_path'],
                  request.form['model_pre_shell'],
                  request.form['model_pos_shell'],
                  env_id])
    g.db.commit()
    return redirect(url_for('build.server_manage'))

"""
@build.route('/war_build/<environment>/<int:page>', methods=['GET'])
@build.route('/war_build/<environment>', methods=['GET'])
@build.route('/war_build', methods=['POST'])
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

    g.db.execute("INSERT INTO builds_record (time, build_desc, operator, process, environment,tomcat) "
                 "VALUES (?, ?, ?, ?, ?, ?)",
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
    return redirect(url_for('build.war_build', environment=request.form['branch'], _method='GET'))
"""


# Jenkins开始构建/完成接口
"""
@build.route('/war_build/update/<branch>/<operation>/<war_name>')
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
"""

# tomcat管理
"""
@build.route("/tomcat_manage")
def tomcat_manage():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("SELECT id, aliid, name, ip_outer, ip_inner, path, port  FROM tomcats ORDER BY id DESC")
    tomcats = cur.fetchall()
    return render_template("tomcat_manage.html",
                           service_type=SERVICE_TYPE["MAIN_SERVICE"],
                           service_name=MAIN_SERVICE["TOMCAT_MANAGE"],
                           tomcats=tomcats)
"""


# 新建tomcat实例
"""
@build.route('/tomcat_new', methods=['POST'])
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
    return redirect(url_for('build.tomcat_manage'))
"""


# 删除实例
"""
@build.route('/tomcat_delete/<tomcat_id>')
def tomcat_delete(tomcat_id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("DELETE FROM tomcats WHERE id=" + tomcat_id)
    g.db.commit()
    return redirect(url_for('build.tomcat_manage'))
"""

# war包管理
"""
@build.route("/war_manage/<environment>", methods=['GET'])
@build.route('/war_manage/<environment>/<int:page>', methods=['GET'])
def war_manage(environment='local_develop', page=1):
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        sources = srv_get_fetcher_containers(environment)
        wars = srv_getwars(environment)
        return render_template('build.war_manage.html',
                               service_type=SERVICE_TYPE["MAIN_SERVICE"],
                               service_name=MAIN_SERVICE["WAR_MANAGE"],
                               page=page,
                               environment=environment,
                               wars=wars,
                               sources=sources)
"""


# 删除war包
"""
@build.route('/war_manage/war_delete/<environment>/<war_name>', methods=['GET'])
def war_delete(war_name, environment='local_develop'):
    if not session.get('logged_in'):
        abort(401)
    srv_war_delete(environment, war_name)
    return redirect(url_for('user.war_manage', environment=environment))
"""


# 新建代码源
"""
@build.route('/war_manage/new_source', methods=['POST'])
def new_source():
    if not session.get('logged_in'):
        abort(401)
    srv_new_source(request.form['environment'], request.form['source_name'], request.form['war'])
    return redirect(url_for('build.war_manage', environment=request.form['environment']))
"""


# 删除代码源
"""
@build.route('/war_manage/delete_source/<source_name>/<environment>')
def delete_source(source_name, environment='local_develop'):
    if not session.get('logged_in'):
        abort(401)
    srv_stop_and_delete_container(source_name)
    return redirect(url_for('build.war_manage', environment=environment))
"""


# 容器管理
"""
@build.route("/container_manage/<environment>", methods=['GET'])
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
"""


# 新建容器
"""
@build.route("/container_manage/new_container", methods=['POST'])
def new_container():
    if not session.get('logged_in'):
        abort(401)
    srv_new_container(request.form['source_name'], request.form['container_name'])
    return redirect(url_for('build.container_manage', environment=request.form['environment']))
"""


# 停止并删除容器
"""
@build.route("/container_manage/<environment>/delete/<container_id>", methods=['GET'])
def stop_and_delete_container(container_id, environment='local_develop'):
    if not session.get('logged_in'):
        abort(401)
    srv_stop_and_delete_container(container_id)
    return redirect(url_for('build.container_manage', environment=environment))
"""




