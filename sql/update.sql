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

-- Переделка таблиц хранения исторических данных #272
alter table `numerical_history` CHANGE COLUMN `value` `value` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_0900_ai_ci' AFTER `type_id`;
rename TABLE `numerical_history` to `values_history`;
rename TABLE `numerical_history_type` to `values_history_type`;

-- Добавить ввод степени упитанности #271
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES (8, 'Степень упитанности', '4');
ALTER TABLE `values_history_type` CHANGE COLUMN `units` `units` VARCHAR(45) NULL COLLATE 'utf8mb4_0900_ai_ci';

-- Состояние слизистой #275
INSERT INTO `values_history_type` (`id`,`name`) VALUES (5, 'Слизистая');
INSERT INTO `manipulations` (`name`, `place_list`) VALUES ('Слизистая', '4');

-- Запись в таблицу animals_dead должна быть уникальной #309
ALTER TABLE `animals_dead` ADD UNIQUE INDEX unique_animal_id (animal_id);

-- Изменить список манипуляций #329
UPDATE `registry_birds`.`manipulations` SET `name`='Энтерофурил' WHERE  `id`=4;
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES
	(11, 'ОАК', '5'),
	(12, 'Биохимия крови', '5'),
	(13, 'Переливание крови', '5'),
	(14, 'Раствор электролитов перорально', '4,5,6'),

-- Диарея: да / нет #276
INSERT INTO `values_history_type` (`id`, `name`, `units`) VALUES (6, 'Диарея', NULL);
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES	(15, 'Диарея', '5,6');

-- Врач: добавить текстовое поле "Другое" #334
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES (16, 'Другое', 5);
INSERT INTO `values_history_type` (`id`, `name`) VALUES (7, 'Другое');

-- В приёмку добавить ввод информации о ловце. #339
ALTER TABLE `animals` ADD COLUMN `catcher` VARCHAR(45) NOT NULL COLLATE 'utf8mb4_0900_ai_ci';

-- Неврологическая симптоматика: да, нет #278
INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES (17, 'Неврологическая симптоматика', '5');
INSERT INTO `values_history_type` (`id`, `name`) VALUES (8, 'Неврологическая симптоматика');
UPDATE `manipulations` SET `name`='Заметка' WHERE  `id`=16;
UPDATE `values_history_type` SET `name`='Заметка' WHERE  `id`=7;

-- Добавить составной уникальный ключ animal_id + datetime для place_history #357
ALTER TABLE `place_history` ADD CONSTRAINT `unique_animal_datetime` UNIQUE (`animal_id`, `datetime`);

-- Добавить составной уникальный ключ animal_id + datetime для place_history #357
ALTER TABLE history ADD CONSTRAINT unique_animal_datetime_manipulation_arm UNIQUE (animal_id, datetime, manipulation_id, arm_id);

INSERT INTO `manipulations` (`name`, `place_list`) VALUES ('Принудительное кормление', '6');
UPDATE `values_history_type` SET `units`='гр.' WHERE  `id`=1;
INSERT INTO `values_history_type` (`name`, `units`) VALUES ('Принудительно съедено', 'гр.');
UPDATE `values_history_type` SET `name`='Съедено' WHERE  `id`=1;