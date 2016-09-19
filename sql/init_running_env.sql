drop table if exists running_env;
create table running_env (
  id integer primary key autoincrement,
  name text,
  server_id integer,
  deploy_time text,
  file_path text,
  pre_shell text,
  pos_shell text
  package_name text
);