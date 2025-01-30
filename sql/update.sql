INSERT INTO `places` (`id`, `name`) VALUES
	(5, 'Нянька');

INSERT INTO `manipulations` (`id`, `name`, `place_list`) VALUES
 (7, 'Взвешивание', '2,5');

INSERT INTO `arms` (`id`, `place_id`, `location_id`) VALUES
(8, 5, 0),
(9, 5, 1);