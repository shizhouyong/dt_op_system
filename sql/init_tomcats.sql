drop table if exists tomcats;
create table tomcats (
  id integer primary key autoincrement,
  aliid text,
  name text not null,
  ip_outer text,
  ip_inner text,
  path text not null,
  port text not null,
  username text not null,
  password text not null
);