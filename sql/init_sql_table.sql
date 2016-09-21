DROP TABLE if EXISTS projects;
CREATE TABLE projects (
    id INTEGER PRIMARY KEY autoincrement,
    project_id INTEGER NOT NULL,
    name text NOT NULL,
    gitlab_url text DEFAULT "",
    branch text DEFAULT "",
    pre_shell text DEFAULT "",
    pos_shell text DEFAULT "",
    time TIMESTAMP NOT NULL,
    status INTEGER NOT NULL DEFAULT 0,
    description text DEFAULT ""
);

DROP TABLE if EXISTS servers;
CREATE TABLE servers (
    id INTEGER PRIMARY KEY autoincrement,
    name text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    ip_outer text,
    ip_inner text,
    environment text NOT NULL
);

DROP TABLE if EXISTS running_env;
CREATE TABLE running_env (
    id INTEGER PRIMARY KEY autoincrement,
    name text DEFAULT "",
    server_id INTEGER NOT NULL,
    deploy_time TIMESTAMP ,
    file_path text NOT NULL,
    pre_shell text DEFAULT "",
    pos_shell text DEFAULT ""
);

DROP TABLE if EXISTS cycles;
CREATE TABLE cycles (
    id INTEGER PRIMARY KEY autoincrement,
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    status INTEGER NOT NULL,
    description text DEFAULT ""
);

DROP TABLE if EXISTS builds_record;
CREATE TABLE builds (
    id INTEGER PRIMARY KEY autoincrement,
    time text NOT NULL,
    build_desc text NOT NULL,
    operator text NOT NULL,
    process text NOT NULL,
    environment text NOT NULL,
    war_name text,
    tomcat INTEGER
);

DROP TABLE if EXISTS deploy_reply;
CREATE TABLE deploy_reply (
    id INTEGER PRIMARY KEY autoincrement,
    time TIMESTAMP,
    reply_uid INTEGER NOT NULL,
    deploy_id INTEGER NOT NULL,
    is_approved INTEGER NOT NULL,
    comment text DEFAULT ""
);

DROP TABLE if EXISTS deploys;
CREATE TABLE deploys (
    id INTEGER PRIMARY KEY autoincrement,
    time TIMESTAMP NOT NULL,
    submitter text NOT NULL,
    reviewer_development text,
    reviewer_production text,
    reviewer_operation text,
    project_id INTEGER NOT NULL,
    builder text,
    deployer text,
    running_env text NOT NULL,
    cycle_id INTEGER,
    status INTEGER NOT NULL DEFAULT 101,
    description text DEFAULT ""
);

DROP TABLE if EXISTS deploy_status;
CREATE TABLE deploy_status (
    id INTEGER PRIMARY KEY DEFAULT 0,
    description text NOT NULL
);

INSERT INTO "deploy_status" VALUES (0, '已提交');
INSERT INTO "deploy_status" VALUES (101, '已通过技术审核');
INSERT INTO "deploy_status" VALUES (102, '已通过产品审核');
INSERT INTO "deploy_status" VALUES (103, '已通过运营审核');
INSERT INTO "deploy_status" VALUES (201, '未通过技术审核');
INSERT INTO "deploy_status" VALUES (202, '未通过产品审核');
INSERT INTO "deploy_status" VALUES (203, '未通过运营审核');
INSERT INTO "deploy_status" VALUES (301, '待构建');
INSERT INTO "deploy_status" VALUES (302, '构建失败');
INSERT INTO "deploy_status" VALUES (401, '待部署');
INSERT INTO "deploy_status" VALUES (402, '部署失败');

DROP TABLE if EXISTS sys_role;
CREATE TABLE sys_role (
    id INTEGER PRIMARY KEY,
    description text NOT NULL
);

DROP TABLE if EXISTS positions;
CREATE TABLE positions(
    id INTEGER PRIMARY KEY autoincrement,
    description text NOT NULL
);

DROP TABLE if EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY autoincrement,
    email text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    sys_role INTEGER NOT NULL,
    position text NOT NULL
);

DROP TABLE if EXISTS project_role;
CREATE TABLE project_role(
    id INTEGER PRIMARY KEY autoincrement,
    description text NOT NULL
);

DROP TABLE if EXISTS project_user_role;
CREATE TABLE project_user_role (
    id INTEGER PRIMARY KEY autoincrement,
		project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    project_role_id INTEGER NOT NULL
);