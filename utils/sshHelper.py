# -*- coding: utf-8 -*-

import paramiko
import configparser
from paramiko import SSHClient


cf = configparser.ConfigParser()
cf.read("../config.iml")


class SSHHelper:

    client = None

    # 这行代码的作用是允许连接不在know_hosts文件中的主机。
    def __init__(self, ip, port, username, password):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(ip, port, username, password)

        #self.client.connect(cf.get("ftpServer", "ip"), int(cf.get("ftpServer", "port")),
        # cf.get("ftpServer", "username"), cf.get("ftpServer", "password"))

    # 执行linux命令
    def exec_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.readlines() + stderr.readlines()

    # 新建文件夹
    def create_folder(self, path, name):
        self.exec_command("cd " + path + " && mkdir " + name)

    # 新建文件
    def create_file(self, path, name):
        self.exec_command("cd " + path + " && touch" + name)

    # 删除文件/文件夹
    def delete_file(self, path, name):
        self.exec_command("cd " + path + " && rm -rf " + name)

    # 复制文件
    def copy_file(self, path1, name1, path2, name2):
        self.exec_command("cp " + path1 + "/" + name1 + " " + path2 + "/" + name2)

    # 新建文件目录
    def create_dir(self, dir_path):
        dir_path_split = dir_path.split("/")
        split_len = dir_path_split.__len__()
        tmp = 1
        dir_path_append = ""
        while tmp < split_len:
            dir_path_append = dir_path_append + "/" + dir_path_split[tmp]
            message = self.exec_command("cd " + dir_path_append)

            if message:
                self.exec_command("mkdir " + dir_path_append)
            tmp += 1


if __name__ == '__main__':
    conn = SSHHelper('192.168.1.237', 22, 'root', 'love0310')
    # conn.create_folder('/srv/ftp', 'jar2')
    # conn.create_file('/srv/ftp/war', 'like')
    # conn.copy_file('/srv/ftp/war', 'like', '/srv/ftp/jar', 'like')
    # conn.create_folder('/srv/ftp/war', '2')
    # conn.delete_file('/srv/ftp', '2')
    dir_path_1 = "/usr/local/tomcat7/vomoho/vomoho-tongji"
    conn.create_dir(dir_path_1)


