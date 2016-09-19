drop table if exists users;
create table users (
  id integer primary key autoincrement,
  email text not null,
  username text not null,
  password text not null,
  system_role integer not null,
  position text not null
);

INSERT INTO users (email, username, password, system_role, position) VALUES ("admin@vomoho.com", "admin", "dt123", 1,"运维管理员");
INSERT INTO users (email, username, password, system_role, position) VALUES ("zhouyong.shi@vomoho.com", "zhouyong.shi", "dt123", 4,"java实习");
INSERT INTO users (email, username, password, system_role, position) VALUES ("ting.wang@vomoho.com", "ting.wang", "dt123", 3,"java开发");
INSERT INTO users (email, username, password, system_role, position) VALUES ("yiqing.zeng@vomoho.com", "yiqing.zeng", "dt123", 2,"测试");