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
INSERT INTO `arms` (`id`, `place_id`, `location_id`) VALUES
	(8, 5, 0),
	(9, 5, 1);