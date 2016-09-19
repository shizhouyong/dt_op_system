from utils import jenkinsHelper

# 定义远程的jenkins master server的url，以及port
jenkins_server_url = 'http://192.168.1.252:32768/'

# 定义用户的User Id 和 API Token，获取方式同上文
user_id = 'xxxx'
api_token='xxxx'

# 实例化jenkins对象，连接远程的jenkins master server
# server = jenkins.Jenkins(jenkins_server_url, username=user_id, password=api_token)
server = jenkinsHelper.Jenkins(jenkins_server_url)
version = server.get_version()
print(version)
jobs = server.get_jobs()
print(jobs)
server.build_job('local_develop')
"""
# 定义jobname
job_name = ''
# 构建job名为job_name的job（不带构建参数）
server.build_job(job_name)

# 定义param_dict
param_dict = ''

# String参数化构建job名为job_name的job, 参数param_dict为字典形式，如：param_dict= {"param1"：“value1”， “param2”：“value2”}
server.build_job(job_name, parameters=param_dict)

# 获取job名为job_name的job的相关信息
server.get_job_info(job_name)

# 获取job名为job_name的job的最后次构建号
server.get_job_info(job_name)['lastBuild']['number']

#获取job名为job_name的job的某次构建的执行结果状态
server.get_build_info(job_name,build_number)['result']

#判断job名为job_name的job的某次构建是否还在构建中
server.get_build_info(job_name,build_number)['building']
"""
