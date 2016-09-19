# -*- coding: utf-8 -*-

from flask import Blueprint, session, abort, g, render_template, request, redirect, url_for, jsonify, json

from utils.config import *
from utils.dbHelper import DbHelper
from utils.jenkinsHelper import JenkinsHelper

project = Blueprint('project', __name__)


# 工程列表
@project.route("/project_list")
def project_list():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute("select * from projects")
    projects = cur.fetchall()
    cur2 = g.db.execute("select * from users")
    users = cur2.fetchall()
    return render_template("project_list.html",
                           service_type=SERVICE_TYPE["PROJECT_MANEGE"],
                           service_name=PROJECT_MANEGE["PROJECT_MANEGE"],
                           projects=projects,
                           users=users)


# 工程管理
@project.route("/get_project_information/<project_pid>", methods=['GET'])
def project_manage(project_pid):
    if not session.get('logged_in'):
        abort(401)
    sql = "SELECT a.id,a.username, c.remark from users a,role_scope b,role c,projects d " \
          "where a.id = b.user_id and b.role_id = c.id and d.pid = b.scope_id and b.scope_id = " + project_pid
    cur = g.db.execute(sql)
    results = cur.fetchall()
    members = []
    for result in results:
        member = {
            "id": result[0],
            "username": result[1],
            "remark": result[2]
        }
        members.append(member)
    response = {"result": members}
    json_str = json.dumps(response)
    return jsonify(result=json_str)


# 新建工程
@project.route("/new_project", methods=['POST'])
def new_project():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute('select id from projects ORDER BY pid DESC')
    num = cur.fetchone()
    if not num:
        pid = 1001
    else:
        pid = num[0] + 1001

    g.db.execute('INSERT INTO projects (pid,name,gitlab_url,branch,pre_shell,pos_shell,description) '
                 'VALUES (?, ?, ?, ?, ?, ?, ?)',
                 [pid,
                  request.form['project_name'],
                  request.form['gitlab_url'],
                  request.form['branch'],
                  request.form['pre_shell'],
                  request.form['pos_shell'],
                  request.form['description']])

    g.db.execute('INSERT INTO role_scope (user_id, role_id, scope_id) VALUES (?, ?, ?)',
                 [session.get('id'),
                  3,
                  pid])
    g.db.commit()

    # 获取jenkinsHelper实例对象
    jenkins_helper = JenkinsHelper(g.cf.get("jenkins", "url"), g.cf.get("jenkins", "username"),
                                   g.cf.get("jenkins", "password"))
    # 在jenkins新建一个job
    jenkins_helper.create_project(request.form['project_name'], request.form['gitlab_url'], request.form['branch'],
                                  request.form['pre_shell'], request.form['pos_shell'])

    return redirect(url_for('project.project_list'))


# 删除工程
@project.route("/delete_project/<project_pid>")
def delete_project(project_pid):
    if not session.get('logged_in'):
        abort(401)
    username = session.get('username')
    userid = DbHelper.getuseridbyname(username)
    role = DbHelper.getrolebyuserid(userid, project_pid)
    if role != 3:
        return "你没有权限删除这个工程"
    project = DbHelper.get_project_by_pid(project_pid)
    # 获取jenkinsHelper实例对象
    jenkins_helper = JenkinsHelper(g.cf.get("jenkins", "url"), g.cf.get("jenkins", "username"),
                                   g.cf.get("jenkins", "password"))
    jenkins_helper.delete_job(project[2])

    g.db.execute("DELETE FROM projects WHERE pid=" + project_pid)
    g.db.commit()
    g.db.execute("DELETE FROM role_scope WHERE scope_id=" + project_pid)
    g.db.commit()

    return redirect(url_for('project.project_list'))


# 更新工程
@project.route("/update_project", methods=['POST'])
def update_project():
    if not session.get('logged_in'):
        abort(401)

    pid = request.form['hidden_project_pid']

    # 获取jenkinsHelper实例对象
    jenkins_helper = JenkinsHelper(g.cf.get("jenkins", "url"), g.cf.get("jenkins", "username"),
                                   g.cf.get("jenkins", "password"))
    # 在jenkins新建一个job
    jenkins_helper.reconfig_job(request.form['project_name'], request.form['gitlab_url'], request.form['branch'],
                                  request.form['pre_shell'], request.form['pos_shell'])

    g.db.execute('UPDATE projects set name = ?,gitlab_url = ?,branch = ?,pre_shell = ?,pos_shell = ?,description = ? '
                 'where pid = ?',
                 [request.form['project_name'],
                  request.form['gitlab_url'],
                  request.form['branch'],
                  request.form['pre_shell'],
                  request.form['pos_shell'],
                  request.form['description'],
                  pid])
    g.db.commit()
    return redirect(url_for('project.project_list'))


# 添加成员
@project.route("/add_member", methods=['POST'])
def add_member():
    if not session.get('logged_in'):
        abort(401)
    project_pid = request.form['hidden_project_pid']
    if project_pid == '1000':
        return redirect(url_for('project.project_list'))
    print(request.form['member'])
    cur = g.db.execute("select id from users where username = '" + request.form['member'] + "'")
    member = cur.fetchone()
    g.db.execute('INSERT INTO role_scope(user_id, role_id, scope_id) values (?, ?, ?)',
                 [member[0],
                  request.form['role'][0],
                  project_pid])
    g.db.commit()
    return redirect(url_for('project.project_list'))


# 删除成员
@project.route("/delete_member/<project_pid>/<member_id>", methods=['GET'])
def delete_member(project_pid, member_id):
    if not session.get('logged_in'):
        abort(401)
    g.db.execute("DELETE FROM role_scope WHERE user_id = " + member_id + " and scope_id = " + project_pid)
    g.db.commit()
    return redirect(url_for('project.project_list'))
