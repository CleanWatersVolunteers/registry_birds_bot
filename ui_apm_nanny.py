from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage
import re

nunny_text_action = 'Выберите действие'
nunny_text_entry_fish = 'Введите количество съеденных рыб'
nunny_text_weighing_action = "Введите массу животного в граммах"
nunny_text_incorrect_digit = "Вводите только цифры"
nunny_text_incorrect_fish_number = "Количество должно быть больше 0"
nunny_text_incorrect_weight = "Вес должна быть от 50"

nunny_cancel = {
    "kbd_cancel":"Отмена",
}

nunny_data = {
    "arm_id": None,
    "title": None,
    "num_feeding_type_id": None,
    "num_weight_type_id": None
}

global_bird_sitter_actions = {
    "bird_sitter_actions": {}
}

def get_numerical_types() -> None:
    numerical_history_type = storage.get_numerical_history_type()
    for item in numerical_history_type:
        if item["name"] == 'Съедено рыбы':
            nunny_data["num_feeding_type_id"] = item["id"]
        elif item["name"] == 'Вес':
            nunny_data["num_weight_type_id"] = item["id"]

def nunny_done_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)

    match = re.search(r'\d+$', key)
    manipulation_id = match.group()
    storage.insert_history(manipulation_id=manipulation_id, animal_id=user["bird"]["bar_code"],
                                   arms_id=nunny_data["arm_id"], tg_nickname=user["id"])
    get_numerical_types()
    if global_bird_sitter_actions["bird_sitter_actions"][key] == 'Кормление':
        user["mode"] = "kbd_mode_feeding"
        text = f'{nunny_text_entry_fish}'
        keyboard = tgm.make_inline_keyboard(nunny_cancel)
        return text, keyboard
    if global_bird_sitter_actions["bird_sitter_actions"][key] == 'Взвешивание':
        user["mode"] = "kbd_mode_weighting"
        text = f'{nunny_text_weighing_action}'
        keyboard = tgm.make_inline_keyboard(nunny_cancel)
        return text, keyboard

    return ui_welcome(user)

def nunny_weighting_hndl(user, key=None, msg=None)->(str,):
    if not msg.isdigit() or int(msg) < 50:
        error_text = nunny_text_incorrect_digit if not msg.isdigit() else nunny_text_incorrect_weight
        text = f'{nunny_data["title"]}:\n{error_text}\n'
        text += nunny_text_weighing_action
        keyboard = tgm.make_inline_keyboard(nunny_cancel)
        return text, keyboard
    else:
        storage.insert_numerical_history(animal_id=user["bird"]["bar_code"], type_id=nunny_data["num_weight_type_id"],
                                     value=int(msg), tg_nickname=user["id"])
    return ui_welcome(user)

def nunny_feeding_hndl(user, key=None, msg=None)->(str,):
    if not msg.isdigit() or int(msg) < 1:
        error_text = nunny_text_incorrect_digit if not msg.isdigit() else nunny_text_incorrect_fish_number
        text = f'{nunny_data["title"]}:\n{error_text}\n'
        text += nunny_text_entry_fish
        keyboard = tgm.make_inline_keyboard(nunny_cancel)
        return text, keyboard
    else:
        storage.insert_numerical_history(animal_id=user["bird"]["bar_code"], type_id=nunny_data["num_feeding_type_id"],
                                     value=int(msg), tg_nickname=user["id"])

    return ui_welcome(user)

############################################
# Global API
############################################
def ui_nanny_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_nunny"
    match = re.search(r'\d+$', key)
    place_id = match.group()
    nunny_data["arm_id"] = storage.get_arm_id(place_id, user["location_id"])
    nunny_data["title"] = ui_welcome_mode[key]
    text = f'{nunny_data["title"]}:\n{nunny_text_action}'

    manipulation_list = storage.get_manipulations(place_id)
    bird_sitter_actions = {f'kbd_mode_nunny_{item["id"]}': f'{item["name"]}' for item in manipulation_list}

    keyboard = tgm.make_inline_keyboard(bird_sitter_actions)
    for key, value in bird_sitter_actions.items():
        welcome_handlers[f"{key}"] = nunny_done_hndl
    global_bird_sitter_actions["bird_sitter_actions"] = bird_sitter_actions
    return text, keyboard

welcome_handlers[f"kbd_mode_feeding"] = nunny_feeding_hndl
welcome_handlers[f"kbd_mode_weighting"] = nunny_weighting_hndl