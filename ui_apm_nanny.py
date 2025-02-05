from ui_welcome import welcome_handlers, ui_welcome_mode, ui_welcome
import tgm
from storage import storage


nanny_minimal_weight = 50
nanny_minimal_fish = 1

# БД manipulations.id
feeding_manipulations_id = 0
weighting_manipulations_id = 7

# БД numerical_history_type.id
feeding_history_type_id = 1
weighting_history_type_id = 2

time_format = "%H:%M"
date_format = "%d.%m.%y"

nanny_text_action = "Выполните необходимые операции и нажмите 'Готово'"
nanny_text_animal_header = "Животное №:"

nanny_done = {
    "kbd_nanny_done": "Готово",
}

nanny_text_entry_fish = 'Введите количество съеденных рыб'
nanny_text_weighing_action = "Введите массу животного в граммах"
nanny_text_incorrect_digit = "Вводите только цифры"
nanny_text_incorrect_fish_number = "Количество должно быть больше 0"
nanny_text_incorrect_weight = f"Вес должен быть от {nanny_minimal_weight} гр."
nanny_manipulations_not_found = "Манипуляции не найдены"

nanny_cancel = {
    "kbd_cancel": "Отмена",
}

nanny_data = {
    "arm_id": None,
    "title": None,
    "place_id": 5,
    "animal_id": None,
    "manipulations": [],
    "manipulations_menu": {},
}


def nanny_done_hndl(user, key=None, msg=None) -> (str,):
    return ui_welcome(user)


def nanny_get_body(user):
    text = f'{nanny_data["title"]}:\n'
    text += f'{nanny_text_animal_header}{user["bird"]["bar_code"]}\n'
    text += f'{manipulation_history_text(nanny_data["animal_id"])}\n'
    text += f'---------------\n{nanny_text_action}'
    return text


############################################
# Global API
############################################
def ui_nanny_mode(user, key=None, msg=None) -> (str,):
    # Инициализируем arm
    nanny_data["arm_id"] = storage.get_arm_id(nanny_data["place_id"], user["location_id"])
    nanny_data["title"] = ui_welcome_mode[key]
    nanny_data["animal_id"] = user["bird"]["animal_id"]
    text = nanny_get_body(user)

    # Динамически обновляем кнопкоменюшку манипуляций по доступным манипуляциям
    nanny_data["manipulations"] = storage.get_manipulations(nanny_data["place_id"])
    kbd_manip_prefix = "kbd_nanny_manip_"
    manipulations_menu = nanny_data['manipulations_menu'] = nanny_done.copy()
    for button in manipulations_menu:
        # Дефолтное меню манипуляций — все ведет на Done.
        welcome_handlers[button] = nanny_done_hndl
    for mannum, manip in enumerate(nanny_data["manipulations"]):
        button_code = f'''{kbd_manip_prefix}_{mannum}'''
        nanny_data['manipulations_menu'][button_code] = f'''{manip['name']}'''
        # Обновляем глобальные идентификаторы кнопок манипуляций.

        if manip['id'] == feeding_manipulations_id:
            welcome_handlers[button_code] = ui_nanny_feeding
            nanny_data["num_feeding_type_id"] = feeding_history_type_id
        elif manip['id'] == weighting_manipulations_id:
            welcome_handlers[button_code] = ui_nanny_weighting
            nanny_data["num_weight_type_id"] = weighting_history_type_id
        else:
            welcome_handlers[button_code] = nanny_manipulations_hndl

    keyboard = tgm.make_inline_keyboard(manipulations_menu)
    return text, keyboard

def ui_nanny_feeding(user, key=None, msg=None) -> (str,):
    user["mode"] = "kbd_mode_feeding"
    text = f'{nanny_text_animal_header}{user["bird"]["bar_code"]}\n{nanny_text_entry_fish}'
    keyboard = tgm.make_inline_keyboard(nanny_cancel)
    return text, keyboard


def ui_nanny_weighting(user, key=None, msg=None) -> (str,):
    user["mode"] = "kbd_mode_weighting"
    text = f'{nanny_text_animal_header}{user["bird"]["bar_code"]}\n{nanny_text_weighing_action}'
    keyboard = tgm.make_inline_keyboard(nanny_cancel)
    return text, keyboard


def manipulation_history_text(animal_id) -> (str,):
    numerical_history = storage.get_animal_numerical_history(animal_id)
    history = storage.get_animal_history(animal_id)
    combined_history = numerical_history + history
    sorted_history = sorted(combined_history, key=lambda item: item['datetime'])
    result_string = ""
    current_date = None
    for item in sorted_history:
        formatted_date = item['datetime'].strftime(date_format)
        if current_date != formatted_date:
            if current_date is not None:
                result_string += "\n"
            result_string += f"{formatted_date}\n"
            current_date = formatted_date
        if 'type_name' in item:  # Элемент из numerical_history
            result_string += f"{item['datetime'].strftime(time_format)} - {item['type_name']}: {item['value']} {item['type_units']} - {item['tg_nickname']}\n"
        else:  # Элемент из history
            result_string += f"{item['datetime'].strftime(time_format)} - {item['manipulation_name']} - {item['tg_nickname']}\n"
    if result_string == "":
        result_string += nanny_manipulations_not_found
    else:
        result_string = result_string.strip()
    return result_string


def nanny_manipulations_hndl(user, key=None, msg=None) -> (str,):
    manip = key.split('__')[1]
    manip_num = int(manip)
    manipulation = nanny_data["manipulations"][manip_num]
    storage.insert_history(manipulation["id"], nanny_data["animal_id"], nanny_data["arm_id"], user["id"])
    text = nanny_get_body(user)
    keyboard = tgm.make_inline_keyboard(nanny_data['manipulations_menu'])
    return text, keyboard


def nanny_feeding_hndl(user, key=None, msg=None) -> (str,):
    if not msg.isdigit() or int(msg) < nanny_minimal_fish:
        error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_fish_number
        text = f'{nanny_data["title"]}:\n{error_text}\n'
        text += nanny_text_entry_fish
        keyboard = tgm.make_inline_keyboard(nanny_cancel)
        return text, keyboard
    else:
        storage.insert_numerical_history(animal_id=nanny_data["animal_id"], type_id=nanny_data["num_feeding_type_id"],
                                         value=int(msg), tg_nickname=user["id"])
        text = nanny_get_body(user)
        keyboard = tgm.make_inline_keyboard(nanny_data['manipulations_menu'])
        return text, keyboard


def nanny_weighting_hndl(user, key=None, msg=None) -> (str,):
    if not msg.isdigit() or int(msg) < nanny_minimal_weight:
        error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_weight
        text = f'{nanny_data["title"]}:\n{error_text}\n'
        text += nanny_text_weighing_action
        keyboard = tgm.make_inline_keyboard(nanny_cancel)
        return text, keyboard
    else:
        storage.insert_numerical_history(animal_id=nanny_data["animal_id"], type_id=nanny_data["num_weight_type_id"],
                                         value=int(msg), tg_nickname=user["id"])
        text = nanny_get_body(user)
        keyboard = tgm.make_inline_keyboard(nanny_data['manipulations_menu'])
        return text, keyboard


welcome_handlers["kbd_nanny_done"] = nanny_done_hndl
welcome_handlers["kbd_mode_feeding"] = nanny_feeding_hndl
welcome_handlers["kbd_mode_weighting"] = nanny_weighting_hndl