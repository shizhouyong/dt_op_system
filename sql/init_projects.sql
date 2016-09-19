drop table if exists projects;
create table projects (
  id integer primary key autoincrement,
  pid integer,
  name text not null,
  gitlab_url text default "",
  branch text default "",
  pre_shell default "",
  pos_shell default "",
  time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  status not null default 0,
  description text default ""
);
