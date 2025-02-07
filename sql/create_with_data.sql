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
  `bar_code` int NOT NULL UNIQUE,
  `registration_datetime` datetime NOT NULL,
  `place_capture` varchar(45) NOT NULL,
  `capture_datetime` datetime NOT NULL,
  `degree_pollution` varchar(45) NOT NULL,
  `weight` int DEFAULT NULL,
  `species` varchar(45) DEFAULT NULL,
  `clinical_condition_admission` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.arms
CREATE TABLE IF NOT EXISTS `arms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `place_id` int NOT NULL,
  `location_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_arms_places1_idx` (`place_id`),
  KEY `fk_arms_locations1_idx` (`location_id`),
  CONSTRAINT `fk_arms_locations1` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`),
  CONSTRAINT `fk_arms_places1` FOREIGN KEY (`place_id`) REFERENCES `places` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.arms: ~8 rows (приблизительно)
INSERT INTO `arms` (`id`, `place_id`, `location_id`) VALUES
	(0, 0, 0),
	(1, 1, 0),
	(2, 2, 0),
	(3, 3, 0),
	(4, 4, 0),
	(5, 0, 1),
	(6, 1, 1),
	(7, 2, 2),
	(8, 5, 0),
	(9, 5, 1);

-- Дамп структуры для таблица registry_birds.history
CREATE TABLE IF NOT EXISTS `history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `manipulation_id` int NOT NULL,
  `arm_id` int NOT NULL,
  `tg_nickname` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_history_animals1_idx` (`animal_id`),
  KEY `fk_history_manipulations1_idx` (`manipulation_id`),
  KEY `fk_history_arms1_idx` (`arm_id`),
  CONSTRAINT `fk_history_animals1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`),
  CONSTRAINT `fk_history_arms1` FOREIGN KEY (`arm_id`) REFERENCES `arms` (`id`),
  CONSTRAINT `fk_history_manipulations1` FOREIGN KEY (`manipulation_id`) REFERENCES `manipulations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.locations
CREATE TABLE IF NOT EXISTS `locations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `address` varchar(45) NOT NULL,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.locations: ~2 rows (приблизительно)
INSERT INTO `locations` (`id`, `address`, `name`) VALUES
	(0, 'Витязево, ул. Жемчужная, д9.', 'Жемчужная'),
	(1, 'Анапа, Пионерский просп.д  68', 'Полярные Зори');

-- Дамп структуры для таблица registry_birds.manipulations
CREATE TABLE IF NOT EXISTS `manipulations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `place_list` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.manipulations: ~7 rows (приблизительно)
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES
	(0, 'Ел сам', '5'),
	(1, 'Пил сам', '5'),
	(2, 'Отказ от еды', '5'),
	(3, 'Отказ от питья', '5'),
	(4, 'Энтерофурил + физ.раствор 20мл в рот', '3,5'),
	(5, 'Рингер 50/50 + Глюкоза 10мл', '3'),
	(6, 'Бриллиантовые глаза', '3'),
	(7, 'Взвешивание', '5');

-- Дамп структуры для таблица registry_birds.numerical_history
CREATE TABLE IF NOT EXISTS `numerical_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `type_id` int NOT NULL,
  `value` int NOT NULL,
  `datetime` datetime NOT NULL,
  `tg_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_numerical_history_numerical_history_type1_idx` (`type_id`),
  KEY `fk_numerical_history_animals1_idx` (`animal_id`),
  CONSTRAINT `fk_numerical_history_animals1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`),
  CONSTRAINT `fk_numerical_history_numerical_history_type1` FOREIGN KEY (`type_id`) REFERENCES `numerical_history_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.numerical_history_type
CREATE TABLE IF NOT EXISTS `numerical_history_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `units` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.numerical_history_type: ~3 rows (приблизительно)
INSERT INTO `numerical_history_type` (`id`, `name`, `units`) VALUES
	(1, 'Съедено рыбы', 'шт.'),
	(2, 'Вес', 'гр.'),
	(3, 'Температура', '°C');

-- Дамп структуры для таблица registry_birds.places
CREATE TABLE IF NOT EXISTS `places` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.places: ~5 rows (приблизительно)
INSERT INTO `places` (`id`, `name`) VALUES
	(0, 'Поступление'),
	(1, 'Первичка на мойке'),
	(2, 'Прием в стационар'),
	(3, 'Первичка в стационаре'),
	(4, 'Медицинский прием'),
	(5, 'Нянька');

-- Дамп структуры для таблица registry_birds.place_history
CREATE TABLE IF NOT EXISTS `place_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `tg_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `arm_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `fk_place_history_animals_idx` (`animal_id`),
  KEY `fk_place_history_arms1_idx` (`arm_id`),
  CONSTRAINT `fk_place_history_animals` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`),
  CONSTRAINT `fk_place_history_arms1` FOREIGN KEY (`arm_id`) REFERENCES `arms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Таблица хранения последнего числа печати
CREATE TABLE IF NOT EXISTS qr_last_number ( 
    id INT PRIMARY KEY DEFAULT 1,  -- фиксированный ID = 1 
    qr_start_value INT NOT NULL);

-- Запись последнего числа печати
INSERT INTO qr_last_number (qr_start_value) VALUES (0);


/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
