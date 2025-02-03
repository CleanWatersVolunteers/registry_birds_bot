from ui_welcome import welcome_handlers, ui_welcome_mode, ui_welcome
import tgm
from storage import storage
import re

nanny_minimal_weight = 50
nanny_minimal_fish = 1

nanny_text_action = 'Выберите действие'
nanny_text_entry_fish = 'Введите количество съеденных рыб'
nanny_text_weighing_action = "Введите массу животного в граммах"
nanny_text_incorrect_digit = "Вводите только цифры"
nanny_text_incorrect_fish_number = "Количество должно быть больше 0"
nanny_text_incorrect_weight = f"Вес должна быть от {nanny_minimal_weight}"

nanny_cancel = {
    "kbd_cancel":"Отмена",
}

nanny_data = {
    "arm_id": None,
    "title": None,
    "num_feeding_type_id": None,
    "num_weight_type_id": None,
    "animal_id": None
}

global_bird_sitter_actions = {
    "bird_sitter_actions": {}
}

def nanny_done_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)

    match = re.search(r'\d+$', key)
    manipulation_id = match.group()
    if global_bird_sitter_actions["bird_sitter_actions"][key] not in ('Кормление', 'Взвешивание'):
        storage.insert_history(manipulation_id=manipulation_id, animal_id=nanny_data["animal_id"],
                                   arms_id=nanny_data["arm_id"], tg_nickname=user["id"])

    else:
        numerical_history_type = storage.get_numerical_history_type()
        for item in numerical_history_type:
            if item["name"] == 'Съедено рыбы':
                nanny_data["num_feeding_type_id"] = item["id"]
            elif item["name"] == 'Вес':
                nanny_data["num_weight_type_id"] = item["id"]

        if global_bird_sitter_actions["bird_sitter_actions"][key] == 'Кормление':
            user["mode"] = "kbd_mode_feeding"
            text = f'{nanny_text_entry_fish}'
            keyboard = tgm.make_inline_keyboard(nanny_cancel)
            return text, keyboard

        else:
            user["mode"] = "kbd_mode_weighting"
            text = f'{nanny_text_weighing_action}'
            keyboard = tgm.make_inline_keyboard(nanny_cancel)
            return text, keyboard


    return ui_welcome(user)

def nanny_weighting_hndl(user, key=None, msg=None)->(str,):
    if not msg.isdigit() or int(msg) < nanny_minimal_weight:
        error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_weight
        text = f'{nanny_data["title"]}:\n{error_text}\n'
        text += nanny_text_weighing_action
        keyboard = tgm.make_inline_keyboard(nanny_cancel)
        return text, keyboard
    else:
        storage.insert_numerical_history(animal_id=nanny_data["animal_id"], type_id=nanny_data["num_weight_type_id"],
                                     value=int(msg), tg_nickname=user["id"])
    return ui_welcome(user)

def nanny_feeding_hndl(user, key=None, msg=None)->(str,):
    if not msg.isdigit() or int(msg) < nanny_minimal_fish:
        error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_fish_number
        text = f'{nanny_data["title"]}:\n{error_text}\n'
        text += nanny_text_entry_fish
        keyboard = tgm.make_inline_keyboard(nanny_cancel)
        return text, keyboard
    else:
        storage.insert_numerical_history(animal_id=nanny_data["animal_id"], type_id=nanny_data["num_feeding_type_id"],
                                     value=int(msg), tg_nickname=user["id"])

    return ui_welcome(user)

############################################
# Global API
############################################
def ui_nanny_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_nunny"
    match = re.search(r'\d+$', key)
    place_id = match.group()
    nanny_data["arm_id"] = storage.get_arm_id(place_id, user["location_id"])
    nanny_data["title"] = ui_welcome_mode[key]
    nanny_data["animal_id"] = storage.get_animal_id(user["bird"]["bar_code"])
    text = f'{nanny_data["title"]}:\n{nanny_text_action}\n'

    manipulation_list = storage.get_manipulations(place_id)
    bird_sitter_actions = {f'kbd_mode_nunny_{item["id"]}': f'{item["name"]}' for item in manipulation_list}
    global_bird_sitter_actions["bird_sitter_actions"] = bird_sitter_actions
    keyboard = tgm.make_inline_keyboard(bird_sitter_actions | nanny_cancel)
    for key, value in bird_sitter_actions.items():
        welcome_handlers[f"{key}"] = nanny_done_hndl
    return text, keyboard

welcome_handlers[f"kbd_mode_feeding"] = nanny_feeding_hndl
welcome_handlers[f"kbd_mode_weighting"] = nanny_weighting_hndl