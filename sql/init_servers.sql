drop table if exists servers;
create table servers (
  id integer primary key autoincrement,
  aliid text,
  name text not null,
  type not null default 0,
  username not null,
  password not null,
  ip_outer text,
  ip_inner text,
  environment text not null
);