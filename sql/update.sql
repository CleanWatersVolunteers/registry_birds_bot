-- Лишний столбец animals.female #102
alter table `animals` drop COLUMN `female`;

-- Исправить записи в таблице manipulations #107
UPDATE `manipulations` SET `place_list`='3,5' WHERE `name`='Бриллиантовые глаза';
UPDATE `manipulations` SET `place_list`='3,5' WHERE `name`='Энтерофурил + физ.раствор 20мл в рот';
UPDATE `manipulations` SET `place_list`='3' WHERE  `name`='Рингер 50/50 + Глюкоза 10мл';

-- Изменить работу с полем "Степень загрязнения" #123
ALTER TABLE `animals` CHANGE COLUMN `degree_pollution` `degree_pollution` varchar(45) NOT NULL

-- Добавить АРМ "Нянька" #80
INSERT INTO `places` (`id`, `name`) VALUES (5, 'Нянька');
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES (7, 'Взвешивание', '5');
UPDATE `registry_birds`.`manipulations` SET `name`='Ел сам' WHERE  `id`=0;
INSERT INTO `arms` (`id`, `place_id`, `location_id`) VALUES
	(8, 5, 0),
	(9, 5, 1);
UPDATE `registry_birds`.`manipulations` SET `place_list`='3' WHERE  `id`=6;

-- Реализовать слой БД для СКУД #162
INSERT INTO `arm_access` (`id`, `arm_id`, `start_date`, `end_date`, `password`) VALUES
	(1, 1, '2025-02-12 00:00:00', '2026-02-12 00:00:00', '1111'),
	(2, 2, '2025-02-12 01:09:39', '2026-02-12 02:09:45', '3333'),
	(3, 3, '2025-03-12 02:10:11', '2025-06-12 02:10:27', '4444');

-- Реализовать АРМ "Старший смены" #197
INSERT INTO `places` (`id`, `name`) VALUES(7, 'Старший смены');
INSERT INTO `arms` (`id`, `place_id`, `location_id`) VALUES (10, 7, 0);
INSERT INTO `arm_access` (`id`, `arm_id`, `start_date`, `end_date`, `password`) VALUES
    (8, 10, '2025-02-20 12:32:32', '2026-02-21 12:32:40', '1010');
