drop table if exists cycles;
create table cycles (
  id integer primary key,
  start integer not null,
  end integer not null,
  status integer default 1 not null,
  create_time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  description text default null
);

insert into cycles(id,start,end, status, description) values (2016081603,20160816,20160903,1,"测试");