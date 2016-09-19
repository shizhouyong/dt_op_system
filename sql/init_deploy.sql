drop table if exists deploys;
create table deploys (
  id integer primary key autoincrement,
  time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  submitter text not null,
  review_develop text,
  review_production text,
  review_operate text,
  project_pid integer not null,
  build_by text,
  deploy_by text,
  running_env text not null default 1,
  cycle_id integer default 0,
  status integer not null default 1,
  description text default null
);
