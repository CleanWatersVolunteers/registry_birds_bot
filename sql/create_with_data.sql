-- --------------------------------------------------------
-- Хост:                         127.0.0.1
-- Версия сервера:               8.0.40 - MySQL Community Server - GPL
-- Операционная система:         Win64
-- HeidiSQL Версия:              12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Дамп структуры базы данных registry_birds
CREATE DATABASE IF NOT EXISTS `registry_birds` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `registry_birds`;

-- Дамп структуры для таблица registry_birds.animals
CREATE TABLE IF NOT EXISTS `animals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bar_code` int NOT NULL,
  `registration_datetime` datetime NOT NULL,
  `place_capture` varchar(45) NOT NULL,
  `capture_datetime` datetime NOT NULL,
  `degree_pollution` int NOT NULL,
  `weight` int DEFAULT NULL,
  `female` binary(1) DEFAULT NULL,
  `species` varchar(45) DEFAULT NULL,
  `clinical_condition_admission` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.arms
CREATE TABLE IF NOT EXISTS `arms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plaсe_id` int NOT NULL,
  `location_id` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `arms` (`id`, `plaсe_id`, `location_id`) VALUES
	(1, 0, 0),
	(2, 1, 0),
	(3, 2, 0),
	(4, 3, 0),
	(5, 4, 0),
	(6, 5, 0),
	(7, 0, 1),
	(8, 1, 1);

-- Дамп структуры для таблица registry_birds.history
CREATE TABLE IF NOT EXISTS `history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `manipulation_id` int NOT NULL,
  `arm_id` int NOT NULL,
  `tg_nickname` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.locations
CREATE TABLE IF NOT EXISTS `locations` (
  `id` int NOT NULL,
  `address` varchar(45) NOT NULL,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `locations` (`id`, `address`, `name`) VALUES
	(0, 'Витязево, ул. Жемчужная, д9.', 'Жемчужная'),
	(1, 'Анапа, Пионерский просп.д  68', 'Полярные Зори');

-- Дамп структуры для таблица registry_birds.manipulations
CREATE TABLE IF NOT EXISTS `manipulations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `place_list` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES
	(1, 'Кормление', '5'),
	(2, 'Поение', '5'),
	(3, 'Отказ от еды', '5'),
	(4, 'Отказ от питья', '5'),
	(5, 'Энтерофурил + физ.раствор 20мл в рот', '2,5');

-- Дамп структуры для таблица registry_birds.numerical_history
CREATE TABLE IF NOT EXISTS `numerical_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `type_id` int NOT NULL,
  `value` int NOT NULL,
  `datetime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.numerical_history_type
CREATE TABLE IF NOT EXISTS `numerical_history_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `units` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `numerical_history_type` (`id`, `name`, `units`) VALUES
	(1, 'Съедено рыбы', 'шт.'),
	(2, 'Вес', 'гр.'),
	(3, 'Температура', '°C');

-- Дамп структуры для таблица registry_birds.place_history
CREATE TABLE IF NOT EXISTS `place_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `tg_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `arm_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.plaсes
CREATE TABLE IF NOT EXISTS `plaсes` (
  `id` int NOT NULL,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.plaсes: ~8 rows (приблизительно)
INSERT INTO `plaсes` (`id`, `name`) VALUES
	(0, 'Поступление'),
	(1, 'Первичка на мойке'),
	(2, 'Прием в стационар'),
	(3, 'Первичка в стационаре'),
	(4, 'Медицинский прием'),
	(5, 'Нянька'),
	(6, 'Загон'),
	(7, 'Гибель');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
