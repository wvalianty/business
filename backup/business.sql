/*
SQLyog Ultimate v11.33 (64 bit)
MySQL - 5.5.53 : Database - business
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE IF NOT EXISTS `business` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `business`;

/*Table structure for table `business_type` */

DROP TABLE IF EXISTS `business_type`;

CREATE TABLE `business_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '业务类型，id',
  `type` char(2) DEFAULT NULL COMMENT '业务类型，大写字母',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;

/*Table structure for table `client` */

DROP TABLE IF EXISTS `client`;

CREATE TABLE `client` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '客户管理表，id',
  `name` varchar(100) DEFAULT NULL COMMENT '客户名称',
  `indate_start` date DEFAULT NULL COMMENT '合同有效开始日期',
  `indate_end` date DEFAULT NULL COMMENT '合同有效截止日期',
  `invoice` varchar(200) DEFAULT NULL COMMENT '发票信息',
  `add_date` datetime DEFAULT NULL COMMENT '添加日期',
  `is_delete` tinyint(1) DEFAULT '0' COMMENT '是否已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;

/*Table structure for table `income` */

DROP TABLE IF EXISTS `income`;

CREATE TABLE `income` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '收入管理，id',
  `income_id` char(6) DEFAULT NULL COMMENT '收入id,生成规则：年份后两位月份比数',
  `client_id` int(11) DEFAULT NULL COMMENT '客户id',
  `business_type` char(2) DEFAULT NULL COMMENT '业务类型',
  `name` varchar(50) DEFAULT NULL COMMENT '业务名称',
  `aff_date` char(7) DEFAULT NULL COMMENT '归属时间, 只保存到月',
  `money` double DEFAULT NULL COMMENT '收入金额',
  `status` tinyint(4) DEFAULT NULL COMMENT '结算进度，0：代开票，1：未回款，2：已回款',
  `media_type` tinyint(4) DEFAULT NULL COMMENT '媒体类型，0：自媒体，1：外媒',
  `cost` varchar(100) DEFAULT NULL COMMENT '渠道成本，媒体类型为外媒才有改项',
  `add_date` datetime DEFAULT NULL COMMENT '添加时间',
  `is_delete` tinyint(1) DEFAULT '0' COMMENT '是否已删除',
  PRIMARY KEY (`id`),
  KEY `client_id` (`client_id`),
  CONSTRAINT `income_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;

/*Table structure for table `income_no` */

DROP TABLE IF EXISTS `income_no`;

CREATE TABLE `income_no` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `income_no` char(6) DEFAULT NULL COMMENT '收入编号',
  `aff_date` varchar(10) DEFAULT NULL COMMENT '所属日期',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

/*Table structure for table `invoice` */

DROP TABLE IF EXISTS `invoice`;

CREATE TABLE `invoice` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '发票管理，id',
  `income_id` VARCHAR(50) NULL  COMMENT '收入id,多个用英文逗号分隔',
  `info` varchar(100) DEFAULT NULL COMMENT '开票信息',
  `add_date` datetime DEFAULT NULL COMMENT '添加时间',
  `finished` tinyint(4) DEFAULT '0' COMMENT '财务确定完成',
  `finished_time` datetime DEFAULT NULL COMMENT '完成时间',
  `is_delete` tinyint(1) DEFAULT '0' COMMENT '是否已删除',
  PRIMARY KEY (`id`),
  KEY `income_id` (`income_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

/*Table structure for table `settlement` */

DROP TABLE IF EXISTS `settlement`;

CREATE TABLE `settlement` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '结算表，id',
  `income_id` int(11) DEFAULT '0' COMMENT '收入表主键id',
  `client_id` int(11) DEFAULT '0' COMMENT '客户id',
  `balance` double DEFAULT '0' COMMENT '结算金额',
  `status` tinyint(4) DEFAULT '0' COMMENT '结算状态， 0：待处理，1：已处理',
  `add_date` datetime DEFAULT NULL COMMENT '添加时间',
  `finished_time` datetime DEFAULT NULL COMMENT '状态，完成时间',
  `is_delete` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `selltement_income_id` (`income_id`),
  KEY `client_id` (`client_id`),
  CONSTRAINT `settlement_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`id`),
  CONSTRAINT `selltement_income_id` FOREIGN KEY (`income_id`) REFERENCES `income` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

/*Table structure for table `syslog` */

DROP TABLE IF EXISTS `users`;
create table users (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `phone` varchar(50) not null,
    `email` varchar(50) not null,
    `passwd` varchar(50) not null,
    `role` tinyint(4) not null COMMENT '0:管理员,1:运营侧,2:财务侧',
    `name` varchar(50) not null,
    `created_at` datetime not null,
    `is_delete` tinyint(1) DEFAULT '0' COMMENT '是否已删除',
    unique key `idx_email` (`email`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

DROP TABLE IF EXISTS `syslog`;

CREATE TABLE `syslog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL  COMMENT '用户',
  `affetced_id`  int(11) DEFAULT NULL COMMENT '受影响id',
  `operate` varchar(10) NOT NULL DEFAULT '' COMMENT '管理员行为:add,update,delete',
  `table` varchar(50) NOT NULL COMMENT '管理员操作的表名，也可以理解为模块',
  `module` varchar(50) DEFAULT '' COMMENT '操作模块',
  `sql` text NOT NULL COMMENT '管理员操作的SQL',
  `add_date` datetime NOT NULL COMMENT '操作时间',
  `is_delete` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`)
) engine=innodb default charset=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


-- ALTER TABLE `business`.`invoice`   CHANGE `income_id` `income_id` VARCHAR(50) NULL  COMMENT '收入id,多个用英文逗号分隔',DROP FOREIGN KEY `invoice_ibfk_1`;

ALTER TABLE `business`.`syslog`   
  ADD COLUMN `is_read` TINYINT(1) DEFAULT 0  NULL  COMMENT '标记是否已读' AFTER `sql`;

ALTER TABLE `business`.`income`   
ADD COLUMN `money_status` TINYINT(1) DEFAULT 0  NULL  COMMENT '回款状态，0：未回款，1：已回款，2：确认回款' AFTER `is_delete`,
ADD COLUMN `inv_status` TINYINT(1) DEFAULT 0  NULL  COMMENT '开票状态：0: 未开票，1：已开票，2：不开票' AFTER `money_status`;

ALTER TABLE `business`.`income`   
  CHANGE `inv_status` `inv_status` TINYINT(1) DEFAULT 0  NULL  COMMENT '开票状态：0: 未开票，1：不开票，2：已开票，';

ALTER TABLE `business`.`income`   
  ADD COLUMN `return_money_date` DATE NULL  COMMENT '回款日期' AFTER `income_company`;
  
  ALTER TABLE `business`.`settlement`   
  ADD COLUMN `stype` TINYINT(1) DEFAULT 0  NULL  COMMENT '结算单类型，0：对公，1：对私' AFTER `finished_time`;