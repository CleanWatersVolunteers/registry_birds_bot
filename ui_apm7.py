from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage
import re

apm7_text_action = 'Выберите действие'
apm7_text_entry_fish = 'Введите количество съеденных рыб'
apm7_text_weighing_action = "Введите массу животного в граммах"
apm7_text_incorrect = "Неверный ввод:"

apm7_cancel = {
    "kbd_cancel":"Отмена",
}

apm7_data = {
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
            apm7_data["num_feeding_type_id"] = item["id"]
        elif item["name"] == 'Вес':
            apm7_data["num_weight_type_id"] = item["id"]

def apm3_done_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)

    match = re.search(r'\d+$', key)
    if match:
        manipulation_id = match.group()

    storage.insert_history(manipulation_id=manipulation_id, animal_id=user["bird"]["bar_code"],
                                   arms_id=apm7_data["arm_id"], tg_nickname=user["id"])
    get_numerical_types()
    if global_bird_sitter_actions["bird_sitter_actions"][key] == 'Кормление':
        user["mode"] = "kbd_mode_apm7_feeding"
        text = f'{apm7_text_entry_fish}'
        keyboard = tgm.make_inline_keyboard(apm7_cancel)
        return text, keyboard
    if global_bird_sitter_actions["bird_sitter_actions"][key] == 'Взвешивание':
        user["mode"] = "kbd_mode_apm7_weighting"
        text = f'{apm7_text_weighing_action}'
        keyboard = tgm.make_inline_keyboard(apm7_cancel)
        return text, keyboard

    return ui_welcome(user)

def apm7_weighting_hndl(user, key=None, msg=None)->(str,):
    if not msg.isdigit() or int(msg) < 50:
        text = f'{apm7_data["title"]}:\n{apm7_text_incorrect} {msg}\n'
        text += apm7_text_weighing_action
        keyboard = tgm.make_inline_keyboard(apm7_cancel)
        return text, keyboard

    else:
        storage.insert_numerical_history(animal_id=user["bird"]["bar_code"], type_id=apm7_data["num_weight_type_id"],
                                     value=int(msg), tg_nickname=user["id"])
    return ui_welcome(user)

def apm7_feeding_hndl(user, key=None, msg=None)->(str,):
    if not msg.isdigit() or int(msg) < 1:
        text = f'{apm7_data["title"]}:\n{apm7_text_incorrect} {msg}\n'
        text += apm7_text_entry_fish
        keyboard = tgm.make_inline_keyboard(apm7_cancel)
        return text, keyboard

    else:
        storage.insert_numerical_history(animal_id=user["bird"]["bar_code"], type_id=apm7_data["num_feeding_type_id"],
                                     value=int(msg), tg_nickname=user["id"])

    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm7_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm7"
    match = re.search(r'\d+$', key)
    if match:
        place_id = match.group()
    apm7_data["arm_id"] = storage.get_arm_id(place_id, user["location_id"])
    apm7_data["title"] = ui_welcome_mode[key]
    text = f'{apm7_data["title"]}:\n{apm7_text_action}'

    manipulation_list = storage.get_manipulations(place_id)
    bird_sitter_actions = {f'kbd_mode_apm7_{item["id"]}': f'{item["name"]}' for item in manipulation_list}

    keyboard = tgm.make_inline_keyboard(bird_sitter_actions)
    for key, value in bird_sitter_actions.items():
        welcome_handlers[f"{key}"] = apm3_done_hndl
    global_bird_sitter_actions["bird_sitter_actions"] = bird_sitter_actions
    return text, keyboard

welcome_handlers[f"kbd_mode_apm7_feeding"] = apm7_feeding_hndl
welcome_handlers[f"kbd_mode_apm7_weighting"] = apm7_weighting_hndl


