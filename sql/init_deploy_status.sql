drop table if exists deploy_status;
create table deploy_status (
    id integer primary key autoincrement,
    remark text not null
);
