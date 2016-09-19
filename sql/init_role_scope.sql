drop table if exists role_scope;
create table role_scope (
    id integer primary key autoincrement,
    user_id integer not null,
    role_id integer not null,
    scope_id integer not null
);

INSERT INTO role_scope (user_id, role_id, scope_id) VALUES (1,3,1001);