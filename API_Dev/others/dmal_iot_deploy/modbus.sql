-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: localhost    Database: modbus
-- ------------------------------------------------------
-- Server version	8.0.29-0ubuntu0.21.10.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `air_conditioner`
--

DROP TABLE IF EXISTS `air_conditioner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `air_conditioner` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_temperature_setpoint` decimal(3,1) DEFAULT NULL,
  `valve_ovr_flag` smallint NOT NULL,
  `valve_ovr_cmd` decimal(4,1) DEFAULT NULL,
  `fcu_ss_ovr_flag` smallint NOT NULL,
  `fcu_ss_ovr_cmd` smallint NOT NULL,
  `fcu_speed_ovr_flag` smallint NOT NULL,
  `fcu_speed_ovr_cmd` smallint NOT NULL,
  `room_temperature_1` decimal(3,1) DEFAULT NULL,
  `room_temperature_2` decimal(3,1) DEFAULT NULL,
  `room_humidity_1` decimal(4,1) DEFAULT NULL,
  `room_humidity_2` decimal(4,1) DEFAULT NULL,
  `bms_local` smallint NOT NULL,
  `fcu_ss_cmd` smallint NOT NULL,
  `fcu_status` smallint NOT NULL,
  `fcu_trip` smallint NOT NULL,
  `fcu_low_speed` smallint NOT NULL,
  `fcu_med_speed` smallint NOT NULL,
  `fcu_high_speed` smallint NOT NULL,
  `off_coil_temperature` decimal(3,1) DEFAULT NULL,
  `water_leakage_status` smallint NOT NULL,
  `chws_temperature` decimal(3,1) DEFAULT NULL,
  `chwr_temperature` decimal(3,1) DEFAULT NULL,
  `chw_flow_rate` smallint NOT NULL,
  `chw_valve_cmd` decimal(4,1) DEFAULT NULL,
  `chw_valve_position` decimal(4,1) DEFAULT NULL,
  `fcu_airflow_rate` smallint NOT NULL,
  `U` decimal(7,3) DEFAULT NULL,
  `I` decimal(7,3) DEFAULT NULL,
  `PF` decimal(6,4) DEFAULT NULL,
  `Phase_Angle` decimal(5,3) DEFAULT NULL,
  `Kvar` decimal(6,2) DEFAULT NULL,
  `time` datetime NOT NULL,
  `W` int DEFAULT NULL,
  `KWH` decimal(9,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf32;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `air_conditioner`
--

LOCK TABLES `air_conditioner` WRITE;
/*!40000 ALTER TABLE `air_conditioner` DISABLE KEYS */;
INSERT INTO `air_conditioner` VALUES (1,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 07:07:07',NULL,NULL),(2,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 07:07:10',NULL,NULL),(3,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 07:08:18',NULL,NULL),(4,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 07:09:20',NULL,NULL),(5,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 14:54:28',NULL,NULL),(6,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 14:55:30',NULL,NULL),(7,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 14:56:38',NULL,NULL),(8,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 14:57:40',NULL,NULL),(9,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 14:58:48',NULL,NULL),(10,23.0,0,0.0,0,0,0,0,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,NULL,NULL,NULL,NULL,NULL,'2022-09-24 14:59:50',NULL,NULL);
/*!40000 ALTER TABLE `air_conditioner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `air_conditioner_last_data`
--

DROP TABLE IF EXISTS `air_conditioner_last_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `air_conditioner_last_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `room_temperature_1` decimal(3,1) DEFAULT NULL,
  `room_temperature_2` decimal(3,1) DEFAULT NULL,
  `room_humidity_1` decimal(4,1) DEFAULT NULL,
  `room_humidity_2` decimal(4,1) DEFAULT NULL,
  `bms_local` smallint NOT NULL,
  `fcu_ss_cmd` smallint NOT NULL,
  `fcu_status` smallint NOT NULL,
  `fcu_trip` smallint NOT NULL,
  `fcu_low_speed` smallint NOT NULL,
  `fcu_med_speed` smallint NOT NULL,
  `fcu_high_speed` smallint NOT NULL,
  `off_coil_temperature` decimal(3,1) DEFAULT NULL,
  `water_leakage_status` smallint NOT NULL,
  `chws_temperature` decimal(3,1) DEFAULT NULL,
  `chwr_temperature` decimal(3,1) DEFAULT NULL,
  `chw_flow_rate` smallint NOT NULL,
  `chw_valve_cmd` decimal(4,1) DEFAULT NULL,
  `chw_valve_position` decimal(4,1) DEFAULT NULL,
  `fcu_airflow_rate` smallint NOT NULL,
  `U` decimal(7,3) DEFAULT NULL,
  `I` decimal(7,3) DEFAULT NULL,
  `PF` decimal(6,4) DEFAULT NULL,
  `Phase_Angle` decimal(5,3) DEFAULT NULL,
  `Kvar` decimal(6,2) DEFAULT NULL,
  `room_temperature_setpoint` decimal(3,1) DEFAULT NULL,
  `valve_ovr_flag` smallint NOT NULL,
  `valve_ovr_cmd` decimal(4,1) DEFAULT NULL,
  `fcu_ss_ovr_flag` smallint NOT NULL,
  `fcu_ss_ovr_cmd` smallint NOT NULL,
  `fcu_speed_ovr_flag` smallint NOT NULL,
  `fcu_speed_ovr_cmd` smallint NOT NULL,
  `time` datetime NOT NULL,
  `W` int DEFAULT NULL,
  `KWH` decimal(11,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf32;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `air_conditioner_last_data`
--

LOCK TABLES `air_conditioner_last_data` WRITE;
/*!40000 ALTER TABLE `air_conditioner_last_data` DISABLE KEYS */;
INSERT INTO `air_conditioner_last_data` VALUES (1,22.8,22.9,46.9,48.5,0,0,1,0,0,0,0,23.0,0,8.9,21.4,11941,12.2,11.5,8469,228.923,7.633,5.0000,0.000,0.00,23.1,0,10.0,0,0,0,0,'2022-09-09 06:33:16',2233,1234561.89);
/*!40000 ALTER TABLE `air_conditioner_last_data` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-10-27  9:22:29
