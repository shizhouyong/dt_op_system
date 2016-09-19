drop table if exists wars;
create table wars (
  id integer primary key autoincrement,
  filename text not NULL
);