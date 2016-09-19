# coding:utf-8

import jenkins
import logging
from utils.xmlUtil import XmlUtil


class JenkinsHelper:

    url = ''
    username = ''
    password = ''

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def conn_jenkins_server(self):
        try:
            # 获得一个jenkins的操作实例
            server = jenkins.Jenkins(self.url, self.username, self.password)
            # server = jenkins.Jenkins(self.url)
            return server
        except Exception:
            logging.warning('login jenkins failed!')
            return None

    def get_job_count(self):
        server = self.conn_jenkins_server()
        print(server.jobs_count())

    def get_job_config(self, job_name):
        server = self.conn_jenkins_server()
        config = server.get_job_config(job_name)
        return config

    def create_project(self, project_name, git_path, git_branch, pre_shell, pos_shell):
        server = self.conn_jenkins_server()
        if server:
            config = XmlUtil.generate_xml(git_path, git_branch, pre_shell, pos_shell)
            # 参数1写的是项目名称，参数2是xml文档
            print(config)
            server.create_job(project_name, config)
            return True
        else:
            return None

    def project_built2(self, project_name, git_branch):  # 这个函数作用是构建项目
        server = self.conn_jenkins_server()
        server.build_job(project_name, {'Branch': git_branch})

    def project_built(self, project_name):  # 这个函数作用是构建项目
        server = self.conn_jenkins_server()
        server.build_job(project_name)

    def check_project_exist(self, project_name):
        server = self.conn_jenkins_server()
        name = server.get_job_name(project_name)
        if name is None:
            return False
        return True

    def delete_job(self, name):
        server = self.conn_jenkins_server()
        server.delete_job(name)

    def reconfig_job(self, project_name, git_path, git_branch, pre_shell, pos_shell):
        server = self.conn_jenkins_server()
        if server:
            config = XmlUtil.generate_xml(git_path, git_branch, pre_shell, pos_shell)
            # 参数1写的是项目名称，参数2是xml文档
            print(config)
            server.reconfig_job(project_name, config.decode('utf-8'))
            return True
        else:
            return None

    @staticmethod
    def get_str_from_xml(file):
        config = open(file, encoding='utf8').read()
        return config

if __name__ == '__main__':
    jenkinsHelper = JenkinsHelper()
    jenkinsHelper.create_project("empty", "git@gitlab.vomoho.com:moho_web/vomoho-fetch.git", "*/develop_fetch")
    # JenkinsHelper.project_built("empty")


