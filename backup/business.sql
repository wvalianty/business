
-- CREATE DATABASE  IF NOT EXISTS `business`  DEFAULT CHARACTER SET utf8 ;

USE `business`;

CREATE TABLE `business_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '业务类型，id',
  `type` char(2) DEFAULT NULL COMMENT '业务类型，大写字母',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `business_type_unique` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;



CREATE TABLE `client` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '客户管理表，id',
  `name` varchar(100) DEFAULT NULL COMMENT '客户名称',
  `indate_start` date DEFAULT NULL COMMENT '合同有效开始日期',
  `indate_end` date  DEFAULT NULL COMMENT  '合同有效截止日期',
  `invoice` varchar(200) DEFAULT NULL COMMENT '发票信息',
  `add_date` datetime DEFAULT NULL COMMENT '添加日期',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;



CREATE TABLE `income` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '收入管理，id',
  `income_id` char(6) DEFAULT NULL COMMENT '收入id,生成规则：年份后两位月份比数',
  `client_id` int(11) DEFAULT NULL COMMENT '客户id',
  `business_type` char(2) DEFAULT NULL COMMENT '业务类型',
  `name` varchar(50) DEFAULT NULL COMMENT '业务名称',
  `aff_date` char(7) DEFAULT NULL COMMENT '归属时间',
  `money` double DEFAULT NULL COMMENT '收入金额',
  `status` tinyint(4) DEFAULT NULL COMMENT '结算进度，0：代开票，1：未回款，2：已回款',
  `media_type` tinyint(4) DEFAULT NULL COMMENT '媒体类型，0：自媒体，1：外媒',
  `cost` varchar(100) DEFAULT NULL COMMENT '渠道成本，媒体类型为外媒才有改项',
  `add_date` datetime DEFAULT NULL COMMENT '添加时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



CREATE TABLE `invoice` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '发票管理，id',
  `client_id` int(11) DEFAULT NULL COMMENT '客户id  删除',
  `income_id` int(11) DEFAULT NULL COMMENT '收入id',
  `info` varchar(100) DEFAULT NULL COMMENT '开票信息',
  `add_date` datetime DEFAULT NULL COMMENT '添加时间',
  `finished` tinyint(4) DEFAULT 0 COMMENT '财务确定完成',
  `finished_time` datetime DEFAULT NULL COMMENT '完成时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `settlement` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '结算表，id',
  `income_id` int(11) DEFAULT NULL COMMENT '收入表主键id',
  `client_id` int(11) DEFAULT NULL COMMENT '客户表主键id',
  `balance` double DEFAULT NULL COMMENT '结算金额',
  `status` tinyint(4) DEFAULT NULL COMMENT '结算状态， 0：待处理，1：已处理',
  `add_date` datetime DEFAULT NULL COMMENT '添加时间',
  `finished_time` datetime DEFAULT NULL  COMMENT '状态，完成时间',
  PRIMARY KEY (`id`),
  KEY `selltement_income_id` (`income_id`),
  KEY `selltement_client_id` (`client_id`),
  CONSTRAINT `selltement_income_id` FOREIGN KEY (`income_id`) REFERENCES `income` (`id`),
  CONSTRAINT `selltement_client_id` FOREIGN KEY (`client_id`) REFERENCES `client` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



CREATE TABLE `syslog` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(200) DEFAULT NULL,
  `operate` varchar(10) NOT NULL DEFAULT '' COMMENT '管理员行为:add,update,delete',
  `table` varchar(50) NOT NULL COMMENT '管理员操作的表名，也可以理解为模块',
  `module` varchar(50) DEFAULT '' COMMENT '操作模块',
  `sql` text NOT NULL COMMENT '管理员操作的SQL',
  `datetime` datetime NOT NULL COMMENT '操作时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=451 DEFAULT CHARSET=utf8mb4;


CREATE TABLE `income_no` (
  `income_no` char(6) DEFAULT NULL COMMENT '收入编号',
  `aff_date` varchar(10) DEFAULT NULL COMMENT '所属日期'
) ENGINE=InnoDB DEFAULT CHARSET=utf8




