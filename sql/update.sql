-- Лишний столбец animals.female #102
alter table `animals` drop COLUMN `female`;

-- Исправить записи в таблице manipulations #107
UPDATE `manipulations` SET `place_list`='3,5' WHERE `name`='Бриллиантовые глаза';
UPDATE `manipulations` SET `place_list`='3,5' WHERE `name`='Энтерофурил + физ.раствор 20мл в рот';
UPDATE `manipulations` SET `place_list`='3' WHERE  `name`='Рингер 50/50 + Глюкоза 10мл';

INSERT INTO `manipulations` values
(7, 'Взвешивание глаза', '2,5');