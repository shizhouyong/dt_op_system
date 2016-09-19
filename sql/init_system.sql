# 以下是目前版本用到的表

# 用户信息表
drop table if exists users;
create table users (
  id integer primary key autoincrement,
  email text not null,  公司邮箱
  username text not null,  用户名，格式例如：ting.wang
  password text not null,  密码，初始密码dt123
  system_role integer not null,  系统权限
  position text not null  职位
);

# 工程信息表
drop table if exists projects;
create table projects (
  id integer primary key autoincrement,
  pid integer,  工程id,四位数字
  name text not null,  工程名
  gitlab_url text default "",  gitlab上的项目地址
  branch text default "",  分支
  pre_shell default "",  构建前脚本
  pos_shell default "",  构建后脚本
  time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  description text default ""  描述
);

# 部署信息表
drop table if exists deploys;
create table deploys (
  id integer primary key autoincrement,
  time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  submitter_id  integer not null,  部署提交者id
  reviewer_id  integer not null,  指定的部署审核者id
  project_id integer not null,  所属工程id
  running_env_id integer,  服务运行环境id(部署时选择运行环境)
  cycle_id integer default 0,  所属迭代周期
  status integer not null default 1,  状态
  description text default null  描述
);

# 服务器表
drop table if exists servers;
create table servers (
  id integer primary key autoincrement,
  aliid text not null,  阿里云id
  name text not null,  服务器名字
  ip_outer text,  外网地址
  ip_inner text,  内网地址
  environment text not null  所属环境（生产|开发）
);

# 服务运行环境信息表
drop table if exists server_deploy;
create table servers (
  id integer primary key autoincrement,
  name text,  名字
  s_id integer,  服务器id
  deploy_time text,  部署时间
  pre_shell text,  部署前脚本
  pos_shell text  部署后脚本
);

# 迭代周期表
drop table if exists cycles;
create table cycles (
  id integer primary key,
  start integer not null,  开始时间，格式：年月日例如：20160816
  end integer not null,   结束时间，格式：年月日例如：20160903
  create_time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  description text default null  描述
);

# 工程-权限表
drop table if exists role_scope;
create table role_scope (
    id integer primary key autoincrement,
    user_id integer not null,  用户id
    role_id integer not null,  角色id
    scope_id integer not null  所属工程id
);

# 权限表
drop table if exists role;
create table role (
    id integer primary key autoincrement,
    remark text not null  角色对应的权限描述
);


