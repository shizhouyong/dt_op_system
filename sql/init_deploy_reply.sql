drop table if exists deploy_reply;
create table deploy_reply (
  id integer primary key autoincrement,
  time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  user_id integer,
  deploy_id integer,
  reply integer,
  comment text default null
);
