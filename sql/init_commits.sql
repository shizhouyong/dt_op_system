drop table if exists commits;
create table commits (
  id integer primary key autoincrement,
  time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  project_pid  integer not null,
  user_id  integer not null,
  description text default null
);

insert into deploys(project_pid,user_id,description) values (1001,1,"测试");