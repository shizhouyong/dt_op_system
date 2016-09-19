drop table if exists role;
create table role (
    id integer primary key autoincrement,
    remark text not null
);

INSERT INTO role (remark) VALUES ("supermanager");
INSERT INTO role (remark) VALUES ("tester");
INSERT INTO role (remark) VALUES ("manager");
INSERT INTO role (remark) VALUES ("ordinary");