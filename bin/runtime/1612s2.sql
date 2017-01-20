set names utf8;


-- ----------------------------------- 1202-测试数据库发布.sql -----------------------------------
delete from s_merchant limit 1;

-- ----------------------------------- 1226-全租户-发货状态.sql -----------------------------------
#测试sql
alter table s_goods add id_code varchar(3) null;


-- ----------------------------------- 1230-全租户-订单表加字段.sql -----------------------------------
-- 订单表加字段
alter table s_order add status char(1) comment '状态';

-- 积分来源
DELETE FROM h_point_source
WHERE       id IN ('39d46879-8d33-ba10-fa97-72aa1c63ea66', '39d46879-8d43-04db-8e98-02e8a48a8819')
            OR name IN ('社区营地', '云客');

INSERT INTO h_point_source(id, name, icon_url, is_deleted)
VALUES      ('39d46879-8d33-ba10-fa97-72aa1c63ea66', '社区营地', 'http://img.myysq.com.cn/predefine/camp.png', 0);

INSERT INTO h_point_source(id, name, icon_url, is_deleted)
VALUES      ('39d46879-8d43-04db-8e98-02e8a48a8819', '云客', 'http://img.myysq.com.cn/predefine/nav-yunke.png', 0);

-- ----------------------------------- 0115-配置库-加角色.sql -----------------------------------
-- 测试
delete from s_order where id=1 limit 1;