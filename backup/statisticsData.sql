/*
SQLyog Ultimate v11.33 (64 bit)
MySQL - 5.7.18-log : Database - adsl
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`adsl` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `adsl`;

/*Table structure for table `statisticsData` */

DROP TABLE IF EXISTS `statisticsData`;

CREATE TABLE `statisticsData` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pushCount` int(11) DEFAULT '0' COMMENT '推送数',
  `pushUserCount` int(11) DEFAULT '0' COMMENT '推送用户数',
  `displayCount` int(11) DEFAULT '0' COMMENT '展示数',
  `displayUserCount` int(11) DEFAULT '0' COMMENT '展示用户数',
  `displayRate` float DEFAULT '0' COMMENT '展示率%',
  `clickCount` int(11) DEFAULT '0' COMMENT '点击数',
  `clickUserCount` int(11) DEFAULT '0' COMMENT '点击用户数',
  `clickUrlCount` int(11) DEFAULT '0' COMMENT '点击链接数',
  `clickCloseCount` int(11) DEFAULT '0' COMMENT '点击关闭按钮数',
  `clickRate` float DEFAULT '0' COMMENT '点击率%',
  `awaitPushUserCount` int(11) DEFAULT '0' COMMENT '待推送用户数',
  `mDisplayUserCount` int(11) DEFAULT '0' COMMENT '手机展示用户数',
  `pcDisplayUserCount` int(11) DEFAULT '0' COMMENT 'PC展示用户数',
  `haveUrlClickCloseCount` int(11) DEFAULT '0' COMMENT '存在连接点击关闭按钮数',
  `noUrlClickCloseCount` int(11) DEFAULT '0' COMMENT '无链接点击关闭按钮数',
  `cDay` date DEFAULT NULL COMMENT '日期',
  `isNeedClearCache` tinyint(1) DEFAULT '0' COMMENT '无用',
  `isNeedDelete` tinyint(1) DEFAULT '0' COMMENT '无用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
