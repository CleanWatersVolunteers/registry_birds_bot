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
  `place_capture` varchar(45) NOT NULL,
  `capture_datetime` datetime NOT NULL,
  `degree_pollution` varchar(45) NOT NULL,
  `weight` int DEFAULT NULL,
  `species` varchar(45) DEFAULT NULL,
  `clinical_condition_admission` varchar(45) DEFAULT NULL,
  `triage` int DEFAULT NULL,
  `catcher` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bar_code` (`bar_code`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.animals_dead
CREATE TABLE IF NOT EXISTS `animals_dead` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `arms_id` int NOT NULL,
  `tg_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `unique_animal_id` (`animal_id`),
  KEY `fk_animal_id` (`animal_id`),
  KEY `fk_arms_id` (`arms_id`),
  CONSTRAINT `fk_animal_id` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_arms_id` FOREIGN KEY (`arms_id`) REFERENCES `arms` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.animals_outside
CREATE TABLE IF NOT EXISTS `animals_outside` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `tg_nickname` varchar(50) NOT NULL,
  `description` varchar(50) NOT NULL,
  `arms_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `id_UNIQUE` (`id`) USING BTREE,
  UNIQUE KEY `unique_animal_id` (`animal_id`)
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

-- Дамп данных таблицы registry_birds.arms: ~9 rows (приблизительно)
INSERT INTO `arms` (`id`, `place_id`, `location_id`) VALUES
	(1, 1, 0),
	(2, 2, 0),
	(3, 3, 0),
	(4, 4, 0),
	(5, 5, 0),
	(6, 6, 0),
	(7, 7, 0),
	(8, 8, 0),
	(9, 8, 1);

-- Дамп структуры для таблица registry_birds.arm_access
CREATE TABLE IF NOT EXISTS `arm_access` (
  `id` int NOT NULL AUTO_INCREMENT,
  `arm_id` int NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `password` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_arm_access_arm_id` (`arm_id`),
  CONSTRAINT `fk_arm_access_arm_id` FOREIGN KEY (`arm_id`) REFERENCES `arms` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.history
CREATE TABLE IF NOT EXISTS `history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `manipulation_id` int NOT NULL,
  `arm_id` int NOT NULL,
  `tg_nickname` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_animal_datetime_manipulation_arm` (`animal_id`,`datetime`,`manipulation_id`,`arm_id`),
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
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.locations: ~2 rows (приблизительно)
INSERT INTO `locations` (`id`, `address`, `name`) VALUES
	(0, 'Анапа, Пионерский просп.д  68', 'Полярные Зори'),
	(1, 'Витязево, ул. Жемчужная, д9.', 'Жемчужная');

-- Дамп структуры для таблица registry_birds.manipulations
CREATE TABLE IF NOT EXISTS `manipulations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `place_list` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.manipulations: ~19 rows (приблизительно)
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES
	(0, 'Ел сам', '6'),
	(1, 'Пил сам', '6'),
	(2, 'Отказ от еды', '6'),
	(3, 'Отказ от питья', '6'),
	(4, 'Энтерофурил', '4,5,6'),
	(5, 'Рингер 10ми + Глюкоза 10мл', '4,5'),
	(6, 'Бриллиантовые глаза', '4'),
	(7, 'Взвешивание', '6'),
	(8, 'Степень упитанности', '4'),
	(9, 'Слизистая', '4'),
	(11, 'ОАК', '5'),
	(12, 'Биохимия крови', '5'),
	(13, 'Переливание крови', '5'),
	(14, 'Раствор электролитов перорально', '4,5,6'),
	(15, 'Диарея', '5,6'),
	(16, 'Заметка', '5'),
	(17, 'Неврологическая симптоматика', '5'),
	(18, 'Смузи', '6'),
	(19, 'Принудительное кормление', '6');

-- Дамп структуры для таблица registry_birds.places
CREATE TABLE IF NOT EXISTS `places` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.places: ~8 rows (приблизительно)
INSERT INTO `places` (`id`, `name`) VALUES
	(1, 'Поступление'),
	(2, 'Первичка на мойке'),
	(3, 'Стационар'),
	(4, 'Первичка в стационаре'),
	(5, 'Медицинский прием'),
	(6, 'Нянька'),
	(7, 'Старший смены'),
	(8, 'Реабилитационный центр');

-- Дамп структуры для таблица registry_birds.place_history
CREATE TABLE IF NOT EXISTS `place_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `datetime` datetime NOT NULL,
  `tg_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `arm_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `unique_animal_datetime` (`animal_id`,`datetime`),
  KEY `fk_place_history_animals_idx` (`animal_id`),
  KEY `fk_place_history_arms1_idx` (`arm_id`),
  CONSTRAINT `fk_place_history_animals` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`),
  CONSTRAINT `fk_place_history_arms1` FOREIGN KEY (`arm_id`) REFERENCES `arms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Таблица хранения последнего числа печати
CREATE TABLE IF NOT EXISTS `qr_last_number` (
  `id` int NOT NULL DEFAULT 1,  -- фиксированный ID = 1
  `qr_start_value` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Запись последнего числа печати
INSERT INTO `qr_last_number` (`qr_start_value`) VALUES (0);

-- Дамп структуры для таблица registry_birds.values_history
CREATE TABLE IF NOT EXISTS `values_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `animal_id` int NOT NULL,
  `type_id` int NOT NULL,
  `value` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `datetime` datetime NOT NULL,
  `tg_nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_animal_type_datetime` (`animal_id`,`type_id`,`datetime`),
  KEY `fk_values_history_values_history_type1_idx` (`type_id`),
  KEY `fk_values_history_animals1_idx` (`animal_id`),
  CONSTRAINT `fk_values_history_animals1` FOREIGN KEY (`animal_id`) REFERENCES `animals` (`id`),
  CONSTRAINT `fk_values_history_values_history_type1` FOREIGN KEY (`type_id`) REFERENCES `values_history_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп структуры для таблица registry_birds.values_history_type
CREATE TABLE IF NOT EXISTS `values_history_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `units` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы registry_birds.values_history_type: ~9 rows (приблизительно)
INSERT INTO `values_history_type` (`id`, `name`, `units`) VALUES
	(1, 'Съедено', 'гр.'),
	(2, 'Вес', 'гр.'),
	(3, 'Температура', '°C'),
	(4, 'Степень упитанности', NULL),
	(5, 'Слизистая', NULL),
	(6, 'Диарея', NULL),
	(7, 'Заметка', NULL),
	(8, 'Неврологическая симптоматика', NULL),
	(9, 'Принудительно съедено', 'гр.');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
