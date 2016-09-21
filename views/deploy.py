# -*- coding: utf-8 -*-

from flask import Blueprint, session, abort, g, render_template, request, redirect, url_for, jsonify, json
from utils.config import *
from utils.dbHelper import DbHelper
from utils.mailHelper import MailHelper
from utils.jenkinsHelper import JenkinsHelper
from utils.sshHelper import SSHHelper
import time

deploy = Blueprint('deploy', __name__)


# 部署管理/新建部署/审核部署/查看部署列表
@deploy.route('/deploy_manage/<int:page>', methods=['POST', 'GET'])
@deploy.route('/deploy_manage', methods=['POST', 'GET'])
def deploy_manage(page=1):
    if not session.get('logged_in'):
        abort(401)
    username = session.get('username')
    user_id = DbHelper.get_id_username(username)
    system_role = DbHelper.get_role_by_name(username)
    if system_role[0] == 1:
        deploys = DbHelper.get_deploys()
        projects = DbHelper.get_projects()
    elif system_role[0] == 2:
        deploys = DbHelper.get_deploys_by_status3()
        projects = DbHelper.get_projects()
    else:
        deploys = DbHelper.get_deploys_by_username(username, user_id[0])
        projects = DbHelper.get_projects_by_username(username)
    running_envs = DbHelper.get_running_envs()
    cycles = DbHelper.get_cycles()
    reviewers = DbHelper.get_users()
    return render_template("deploy_list.html",
                           service_type=SERVICE_TYPE["DEPLOY_SERVICE"],
                           service_name=DEPLOY_SERVICE["DEPLOY_MANEGE"],
                           page=page,
                           deploys=deploys,
                           projects=projects,
                           running_envs=running_envs,
                           cycles=cycles,
                           reviewers=reviewers,
                           system_role=system_role[0])


# 部署审核-查看详情
@deploy.route('/deploy_review/<int:did>', methods=['GET'])
def deploy_review(did):
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("select a.*, b.username, b.system_role from deploy_reply a,users b where a.user_id = b.id "
                       "and a.deploy_id = " + str(did))
    deploy_replys = cur.fetchall()
    return render_template("deploy_details.html",
                           service_type=SERVICE_TYPE["DEPLOY_SERVICE"],
                           service_name=DEPLOY_SERVICE["DETAILS_DEPLOY"],
                           deploy_replys=deploy_replys)


# 部署管理-拒绝
@deploy.route("/deploy_refuse", methods=['POST'])
def deploy_refuse():
    if not session.get('logged_in'):
        abort(401)
    deploy_id = request.form['deploy_id']
    user_id = DbHelper.getuseridbyname(session.get('username'))
    g.db.execute("update deploys set status = 2 where id = '" + str(deploy_id) + "'")
    g.db.commit()
    g.db.execute("insert into deploy_reply(time, user_id, deploy_id, reply, comment) values (?, ?, ?, ?, ?)",
                [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                 user_id,
                 deploy_id,
                 1,
                 request.form['comment']])
    g.db.commit()
    deploy = DbHelper.get_deploy_by_id(deploy_id)
    print()
    response = {"result": 200}
    json_str = json.dumps(response)
    print(deploy[3])
    mail_helper = MailHelper(deploy[3] + "你有个构建任务被拒绝" + "\n" +
                             "http://192.168.1.101:5000/deploy/deploy_manage?item=ALL_DEPLOY", "构建通知")
    id = DbHelper.get_id_username(deploy[3])
    user = DbHelper.get_users_by_id(id[0])
    mail = user[1]
    print(mail)
    mail_helper.send(mail)
    return jsonify(result=json_str)


# 部署管理-批准
@deploy.route("/deploy_approved", methods=['POST'])
def deploy_approved():
    if not session.get('logged_in'):
        abort(401)
    deploy_id = request.form['deploy_id']
    user_id = DbHelper.getuseridbyname(session.get('username'))
    g.db.execute("update deploys set status = 3 where id = '" + str(deploy_id) + "'")
    g.db.commit()
    g.db.execute("insert into deploy_reply(time, user_id, deploy_id, reply, comment) values (?, ?, ? ,?, ?)",
                 [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  user_id,
                  deploy_id,
                  0,
                  request.form['comment']])
    g.db.commit()
    response = {"result": 200}
    json_str = json.dumps(response)

    user = DbHelper.get_user_by_system_role(2)
    mail_helper = MailHelper(user[2] + "你有个构建任务" + "\n" +
                             "http://192.168.1.101:5000/deploy/deploy_manage?item=ALL_DEPLOY", "构建通知")
    mail = user[1]
    print(mail)
    mail_helper.send(mail)

    return jsonify(result=json_str)


# 部署管理-jenkins构建
@deploy.route("/build_jenkins", methods=['POST'])
def build_jenkins():
    if not session.get('logged_in'):
        abort(401)
    deploy_id = request.form['deploy_id']
    project_name = request.form['project_name']
    project = DbHelper.get_project_by_projectname(project_name)
    name = project[2]
    user_id = DbHelper.getuseridbyname(session.get('username'))
    gitlab_url = project[3]
    branch = "*/" + project[4]
    pre_shell = project[5]
    pos_shell = project[6]

    # 获取jenkinsHelper实例对象
    jenkins_helper = JenkinsHelper(g.cf.get("jenkins", "url"), g.cf.get("jenkins", "username"),
                                   g.cf.get("jenkins", "password"))

    # 判断jenkins里是否存在该工程,存在直接构建;不存在，先新建再构建
    if jenkins_helper.check_project_exist(project_name):
        jenkins_helper.project_built(project_name)
    else:
        return;

    # 获取此工程的总构建数，以此获取该工程此次构建的build_num
    cur = g.db.execute("SELECT COUNT(*) FROM builds_record WHERE pid ='" + str(project[1]) + "'")
    build_num = cur.fetchone()[0] + 1

    build_result = None
    tmp = 0
    while not build_result:
        time.sleep(5)
        build_result = jenkins_helper.get_build_info(project_name, build_num)
        tmp += 1
        if tmp == 20:
            break

    g.db.execute("UPDATE deploys SET status=41 WHERE id = '" + str(deploy_id) + "'")

    if build_result == 'SUCCESS':
        g.db.execute("INSERT INTO builds_record (pid, time, build_desc, oprator, process, environment, tomcat) VALUES(?,?,?,?,?,?,?)",
                     [
                         project[1],
                         time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                         '测试',
                         session.get('username'),
                         '构建成功',
                         'master',
                         '1'
                     ])
        g.db.execute("UPDATE deploys SET status=5001 WHERE id = '" + str(deploy_id) + "'")
    else:
        g.db.execute("INSERT INTO builds_record (pid, time, build_desc, operator, process, environment, tomcat) VALUES(?,?,?,?,?,?,?)",
                    [
                        project[1],
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        '测试',
                        session.get('username'),
                        '构建失败',
                        'master',
                        '1'
                    ])
        g.db.execute("UPDATE deploys SET status = 4 WHERE id = '" + str(deploy_id) + "'")

    g.db.commit()
    g.db.execute("insert into deploy_reply(time, user_id, deploy_id, reply) values (?, ?, ? ,?)",
                 [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  user_id,
                  deploy_id,
                  0])
    g.db.commit()
    response = {"result": 200}
    json_str = json.dumps(response)
    return jsonify(result=json_str)


# 部署管理-开始部署
@deploy.route("/deploy_launch", methods=['POST'])
def deploy_launch():
    if not session.get('logged_in'):
        abort(401)

    deploy_id = request.form['deploy_id']
    env_name = request.form['env_name']

    deploy = DbHelper.get_deploy_by_id(deploy_id)
    env = DbHelper.getenv_info_by_name(env_name)
    server_outer = DbHelper.get_server_by_id(env['server_id'])

    deploy_file_path = env['file_path']
    deploy_pre_shell = env['pre_shell']
    deploy_pos_shell = env['pos_shell']

    # 连接本地服务器
    conn_local = SSHHelper('192.168.1.237', 22, 'root', 'love0310')
    conn_local.exec_command(deploy_pre_shell)

    # 连接项目即将要部署到的服务器
    conn_outer = SSHHelper(server_outer['ip_outer'], 22, server_outer['username'], server_outer['password'])
    conn_outer.create_dir(deploy_file_path)
    conn_outer.exec_command(deploy_pos_shell)
    print(deploy_file_path)
    print(server_outer['ip_outer'])
    print(server_outer['username'])
    print(server_outer['password'])

    response = {"result": 200}
    json_str = json.dumps(response)
    return jsonify(result=json_str)


# 部署管理-删除部署
@deploy.route("/deploy_delete", methods=['POST'])
def deploy_delete():
    if not session.get('logged_in'):
        abort(401)
    deploy_id = request.form['deploy_id']
    g.db.execute("delete from deploys where id = " + str(deploy_id))
    g.db.commit()
    g.db.execute("delete from deploy_reply where id = " + str(deploy_id))
    g.db.commit()
    response = {"result": 200}
    json_str = json.dumps(response)
    return jsonify(result=json_str)


# 部署管理-归档
@deploy.route("/deploy_store", methods=['POST'])
def deploy_store():
    if not session.get('logged_in'):
        abort(401)
    deploy_id = request.form['deploy_id']
    g.db.execute("update deploys set status = 7001 where id = '" + str(deploy_id) + "'")
    g.db.commit()
    response = {"result": 200}
    json_str = json.dumps(response)
    return jsonify(result=json_str)


# 新建部署
@deploy.route("/new_deploy", methods=['POST'])
def new_deploy():
    if not session.get('logged_in'):
        abort(401)
    reviewer_id = DbHelper.get_id_username(request.form['reviewer'])
    project_id = DbHelper.get_id_project_name(request.form['project_name'])
    cycle_id = request.form['cycle']
    description = request.form['description']
    user_id = DbHelper.getuseridbyname(session.get('username'))
    g.db.execute('INSERT INTO deploys(submitter,review_develop,project_pid,cycle_id,description) '
                 'values (?, ?, ?, ?, ?)',
                 [session.get('username'),
                  request.form['reviewer'],
                  project_id[0],
                  cycle_id,
                  description])
    g.db.commit()
    cur = g.db.execute("select id from deploys order by id desc")
    deploy_id = cur.fetchone()
    g.db.execute("insert into deploy_reply(time, user_id, deploy_id, reply) values (?, ?, ? ,?)",
                 [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  user_id,
                  deploy_id[0],
                  0])
    g.db.commit()
    mail_helper = MailHelper(request.form['reviewer']+"这里有个部署需要你去审核" + "\n" +
                             "http://192.168.1.101:5000/deploy/deploy_manage?item=ALL_DEPLOY", "部署审核通知")
    user = DbHelper.get_users_by_id(reviewer_id[0])
    receiver = user[1]
    if receiver != 'admin@vomoho.com':
        mail_helper.send(receiver)
    return redirect(url_for('deploy.deploy_manage', item='ALL_DEPLOY'))


@deploy.route("/select_project", methods=['POST'])
def select_project():
    if not session.get('logged_in'):
        abort(401)
    project_name = request.form['project_name']
    project_pid = DbHelper.get_id_project_name(project_name)
    cur = g.db.execute("SELECT a.username from users a, role_scope b where a.id = b.user_id and b.scope_id = " +
                 str(project_pid[0]) + " and b.role_id = 3")
    results = cur.fetchall()
    managers = []
    for result in results:
        member = result[0]
        managers.append(member)
    response = {"result": managers}
    json_str = json.dumps(response)
    return jsonify(result=json_str)

if __name__ == '__main__':
    print()
