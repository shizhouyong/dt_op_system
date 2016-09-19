# -*- coding: utf-8 -*-

import threading
from time import sleep

import paramiko
from docker import Client
from paramiko import SSHClient
from flask import g
import configparser

cf = configparser.ConfigParser()
cf.read("config.iml")


# 测试,查看252上所有容器
def test_ssh():
    cli = Client(base_url='tcp://192.168.1.252:2375')
    result = cli.containers(all=True)
    for container in result:
            print(container, end="\n")


# 获取指定环境的war包
def srv_getwars(environment):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(cf.get("ftpServer", "ip"), cf.get("ftpServer", "port"), cf.get("ftpServer", "username"), cf.get("ftpServer", "password"))
    stdin, stdout, stderr = client.exec_command('cd /srv/ftp/wars/' + environment + ' && ls')
    files = []
    out = stdout.readlines()
    for line in out:
        if line != 'vomoho.war\n':
            files.extend([line.rstrip('\n')])
    files.sort(reverse=True)
    return files


# 删除ftp上的war包
def srv_war_delete(environment, war):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(cf.get("ftpServer", "ip"), cf.get("ftpServer", "port"), cf.get("ftpServer", "username"), cf.get("ftpServer", "password"))
    client.exec_command('rm /srv/ftp/wars/' + environment + '/' + war)
    client.close()


# 新建代码源
def srv_new_source(environment, source_name, war):
    # 复制一份成为vomoho.war
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(cf.get("ftpServer", "ip"), cf.get("ftpServer", "port"), cf.get("ftpServer", "username"), cf.get("ftpServer", "password"))
    client.exec_command('cp /srv/ftp/wars/' + environment + '/' + war + ' /srv/ftp/wars/' + environment + '/vomoho.war')
    # 创建warfetcher容器
    cli = Client(base_url='tcp://%s:%s' % (cf.get("ftpServer", "ip"), cf.get("ftpServer", "server_port")))
    container = cli.create_container(image='dt/warfetcher', tty=True, name=source_name, command='ftp://%s/wars/%s/vomoho.war' % (cf.get("ftpServer","ip"),environment))
    cli.start(container=container.get('Id'))


# 根据指定代码源新建容器
def srv_new_container(source_name, container_name):
    cli = Client(base_url='tcp://%s:%s' % (cf.get("ftpServer", "ip"), cf.get("ftpServer", "server_port")))
    container = cli.create_container(image='dt/tomcat7', name=container_name, detach=True, host_config=cli.create_host_config(
            publish_all_ports=True, volumes_from=[source_name]
    ))
    cli.start(container=container.get('Id'))
    new_container = cli.containers(latest=True)
    new_port = new_container[0].get('Ports')[0].get('PublicPort')
    thread = MyThread(new_port)
    thread.start()


# 获取所有的dt/warfetcher容器
def srv_get_fetcher_containers(environment):
    fetchers = []
    if environment == 'local_develop':
        cli = Client(base_url='tcp://%s:%s' % (cf.get("ftpServer", "ip"), cf.get("ftpServer", "server_port")))
        result = cli.containers(all=True)
        for container in result:
            if container.get('Image') == 'dt/warfetcher':
                fetchers.append(container)
    # print(fetchers)
    return fetchers


# 获取所有的dt/tomcat7容器
def srv_get_tomcat_containers(environment):
    fetchers = []
    if environment == 'local_develop':
        cli = Client(base_url='tcp://%s:%s' % (cf.get("ftpServer", "ip"), cf.get("ftpServer", "server_port")))
        result = cli.containers(all=True)
        for container in result:
            if container.get('Image') == 'dt/tomcat7':
                fetchers.append(container)
    # print(fetchers)
    return fetchers


# 停止容器并删除
def srv_stop_and_delete_container(container_id):
    cli = Client(base_url='tcp://%s:%s' % (cf.get("ftpServer", "ip"), cf.get("ftpServer", "server_port")))
    # 先找到通过id查询该容器端口,将其从nginx配置中移除
    result = cli.containers(all=True)
    for container in result:
        if container.get('Id') == container_id:
            srv_delete_nginx_server(container.get('Ports')[0].get('PublicPort'))
    # 停止并移除容器
    cli.stop(container_id)
    cli.remove_container(container_id)


# 在nginx中添加服务器
def srv_add_nginx_server(port):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(cf.get("ftpServer", "ip"), cf.get("ftpServer", "port"), cf.get("ftpServer", "username"), cf.get("ftpServer", "password"))
    client.exec_command("sed -i '/ip_hash;/a \server localhost:" + str(port) + ";' /usr/local/nginx/conf/nginx.conf")
    client.exec_command("nginx -s reload")


# 在nginx中删除服务器
def srv_delete_nginx_server(port):
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(cf.get("ftpServer", "ip"), cf.get("ftpServer", "port"), cf.get("ftpServer", "username"), cf.get("ftpServer", "password"))
    client.exec_command("sed -i '/server localhost:" + str(port) + "/d' /usr/local/nginx/conf/nginx.conf")
    client.exec_command("nginx -s reload")


# 延迟180s线程,防止tomcat过早被配置进nginx
class MyThread (threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        sleep(180)
        srv_add_nginx_server(self.port)


class TomcatPublishThread(threading.Thread):
    def __init__(self, environment, filename, path, ip, username, password):
        threading.Thread.__init__(self)
        self.environment = environment
        self.filename = filename
        self.path = path
        self.ip = ip
        self.username = username
        self.password = password

    def run(self):
        print("start")
        tomcat_start(self.environment, self.filename, self.path, self.ip, self.username, self.password)


def publish_tomcat(enviroment, filename, war_id):
    cur = g.db.execute("SELECT * FROM tomcats WHERE id=%d" % war_id)
    tomcat = cur.fetchone()
    if tomcat[3] and tomcat[3] != '':
        ip = tomcat[3]
    else:
        ip = tomcat[4]
    path = tomcat[5]
    username = tomcat[7]
    password = tomcat[8]
    thread = TomcatPublishThread(enviroment, filename, path, ip, username, password)
    thread.start()


def tomcat_start(enviroment, filename, path, ip, username, password):
    try:
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect("192.168.1.252", 22, "root", "menghu123")
        sftp1 = client.open_sftp()
        remote = "/srv/ftp/wars/%s/%s" % (enviroment, filename)
        local = "/usr/local/wars/%s/%s" % (enviroment, filename)
        print("begin scp1")
        sftp1.get(remote, local)

        client.close()

        client.connect(ip, 22, username, password)
        print("ssh")
        stdin, stdout, stderr = client.exec_command("ps -ef|grep %s|grep -v \"grep\"|awk \'{print $2}\'" % path)
        pid = stdout.readlines()
        if pid:
            print(pid)
            client.exec_command("kill -9 %s" % pid[0].replace("\n", ""))
        client.exec_command("rm -rf %s/webapps/vomoho" % path)
        client.exec_command("rm -rf %s/webapps/vomoho.war" % path)
        print("after rm")
        #client.exec_command("scp root@192.168.1.152:/srv/ftp/wars/%s/%s  %s/webapps/vomoho.war" % (enviroment, filename, path))
        #sftp = paramiko.SFTPClient.from_transport(client.get_transport())
        sftp = client.open_sftp()
        local = "/usr/local/wars/%s/%s" % (enviroment, filename)
        remote = "%s/webapps/vomoho.war" % path
        print("begin scp")
        sftp.put(local, remote)

        # stdin, stdout, stderr = client.exec_command("cp /usr/local/wars/%s/%s  %s/webapps/vomoho.war" % (enviroment, filename, path))
        # print(stdout.readlines())
        # print("scp finish")
        #sftp.close()
        sleep(5)
        print("%s/bin/startup.sh" % path)
        stdin, stdout, stderr = client.exec_command("%s/bin/startup.sh" % path)
        print(stdout.readlines())
        print("starttomcat finish")
        print("curl http://%s:%s/war_build/update/%s/%s/%s" % (cf.get("server", "ip"), cf.get("server", "server_port"), enviroment, "published", filename))
        client.exec_command("curl http://%s:%s/war_build/update/%s/%s/%s" % (cf.get("server", "ip"), cf.get("server", "server_port"), enviroment, "published", filename))
        #client.exec_command("exit")
        print(stdout.readlines())
    finally:
        client.close()
    # g.db = connect_db2()
    # g.db.execute("UPDATE builds_record SET process = '发布完毕' WHERE war_name = " + filename)
    # g.db.commit()
    # g.db.close()

    #redirect(url_for('/war_build/update/%s/%s/%s' % (enviroment, "published", filename)))

# srv_get_fetcher_containers('local_develop')
# test_ssh()
# getwars('local_develop')
