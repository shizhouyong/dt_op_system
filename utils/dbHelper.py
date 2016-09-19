# -*- coding: utf-8 -*-

from flask import g


# DB工具类
class DbHelper:

    @classmethod
    def get_users(cls):
        cur = g.db.execute("select * from users")
        return cur.fetchall()

    @classmethod
    def get_users_by_id(cls, uid):
        cur = g.db.execute("select * from users where id = " + str(uid))
        return cur.fetchone()

    @classmethod
    def get_projects(cls):
        cur = g.db.execute("select * from projects")
        return cur.fetchall()

    @classmethod
    def get_project_by_pid(cls, pid):
        cur = g.db.execute("select * from projects where pid = " + str(pid))
        return cur.fetchone()

    @classmethod
    def get_projects_by_username(cls, name):
        cur = g.db.execute("select a.* from projects a,role_scope b,users c where a.pid = b.scope_id "
                           "and b.user_id = c.id and c.username = '" + name + "'")
        return cur.fetchall()

    @classmethod
    def get_project_by_projectname(cls, name):
        cur = g.db.execute("select * from projects where name = '" + name + "'")
        return cur.fetchone()

    @classmethod
    def get_deploys(cls):
        cur = g.db.execute("SELECT a.*, b.name project_name FROM deploys a,projects b where a.project_pid = b.pid")
        return cur.fetchall()

    @classmethod
    def get_deploys_by_status3(cls):
        cur = g.db.execute("SELECT a.*, b.name project_name FROM deploys a,projects b where a.project_pid = b.pid "
                           "and status > 2")
        return cur.fetchall()

    @classmethod
    def get_deploys_by_username(cls, name, user_id):
        sql = "SELECT a.*, b.name project_name,c.role_id role " \
              "FROM (SELECT * from deploys where review_develop = '" + name + "') a,projects b,role_scope c " \
              "WHERE a.project_pid = b.pid and a.project_pid = c.scope_id and c.user_id = '" + str(user_id) + "'"\
              "UNION " \
              "SELECT a.*, b.name project_name,c.role_id role " \
              "FROM (SELECT * from deploys where submitter = '" + name + "') a,projects b,role_scope c " \
              "WHERE a.project_pid = b.pid and a.project_pid = c.scope_id and c.user_id = '" + str(user_id) + "'"
        cur = g.db.execute(sql)
        return cur.fetchall()

    @classmethod
    def get_deploy_by_id(cls, id):
        cur = g.db.execute("SELECT a.*, b.name project_name FROM deploys a,projects b where a.project_pid = b.pid"
                           " and a.id = " + str(id))
        return cur.fetchone()

    @classmethod
    def get_cycles(cls):
        cur = g.db.execute("select * from cycles")
        return cur.fetchall()

    @classmethod
    def get_servers(cls):
        cur = g.db.execute("select * from servers")
        return cur.fetchall()

    @classmethod
    def get_running_envs(cls):
        cur = g.db.execute("select * from running_env")
        return cur.fetchall()

    @classmethod
    def get_user_in_project(cls, project_id):
        cur = g.db.execute("select * from users a,role_scope b where a.id = b.user_id and b.scope_id = " + project_id)
        return cur.fetchall()

    @classmethod
    def getuseridbyname(cls, username):
        cur = g.db.execute("select id from users where username = '" + username + "'")
        result = cur.fetchone()
        userid = result[0]
        return userid

    @classmethod
    def getrolebyuserid(cls, userid, project_pid):
        if userid == 1:
            return 3
        cur = g.db.execute("select role_id from role_scope where user_id = " + str(userid) + " and scope_id = " +
                           str(project_pid))
        result = cur.fetchone()
        if result:
            role = result[0]
        else:
            role = 0
        return role

    @classmethod
    def getProjectNum(cls):
        cur = g.db.execute("select count(*) from projects")
        count = (cur.fetchone())[0]
        return count

    @classmethod
    def get_id_username(cls, name):
        cur = g.db.execute("select id from users where username = '" + name + "'")
        return cur.fetchone()

    @classmethod
    def get_id_server_name(cls, name):
        cur = g.db.execute("select id from servers where name = '" + name + "'")
        return cur.fetchone()

    @classmethod
    def get_id_project_name(cls, name):
        cur = g.db.execute("select pid from projects where name = '" + name + "'")
        return cur.fetchone()

    @classmethod
    def get_role_id_by_remark(cls, remark):
        cur = g.db.execute("select id from role where remark = '" + remark + "'")
        return cur.fetchone()

    @classmethod
    def get_role_by_name(cls, name):
        cur = g.db.execute("select system_role from users where username = '" + name + "'")
        return cur.fetchone()

    @classmethod
    def get_user_by_system_role(cls, role):
        cur = g.db.execute("select * from users where system_role = " + str(role))
        return cur.fetchone()

    @classmethod
    def get_times_of_deploy_in_cycle(cls, cycle_id, user_id):
        cur = g.db.execute("SELECT count(*) from deploys where cycle_id = " + cycle_id + " and submitter_id = " +
                           user_id)
        return cur.fetchone()

    @classmethod
    def get_server_id_by_name(cls, name):
        cur = g.db.execute("SELECT id from servers where name = '" + name + "'")
        return cur.fetchone()

    @classmethod
    def get_env_by_server_id(cls, server_id):
        cur = g.db.execute("SELECT * from running_env where server_id = " + str(server_id))
        return cur.fetchall()

    @classmethod
    def get_env_info_by_id(cls, env_id):
        cur = g.db.execute("SELECT * from running_env where id = " + str(env_id))
        return cur.fetchone()

