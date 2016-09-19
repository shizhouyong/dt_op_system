drop table if exists builds_record;
create table builds_record (
  id integer primary key autoincrement,
  time text not null,
  build_desc text not null,
  operator text not null,
  process text not null,
  environment text NOT NULL,
  war_name text,
  tomcat integer
);
