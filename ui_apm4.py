from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage
import re

apm4_text_action = "Введите массу животного в граммах"
apm4_text_incorrect = "Неверный ввод:"

apm4_cancel = {
    "kbd_cancel":"Отмена",
}

apm4_data = {
    "arm_id": None,
    "title": None
}

def apm4_done_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)
    if not msg.isdigit():
        text = f'{apm4_data["title"]}:\n{apm4_text_incorrect} {msg}\n'
        text += apm4_text_action
        keyboard = tgm.make_inline_keyboard(apm4_cancel)
        return text, keyboard
    storage.insert_place_history(apm4_data["arm_id"], user["bird"]["bar_code"], user["id"])
    storage.update_animal(user["bird"]["bar_code"], weight = msg)
    user["mode"] = None
    user["bird"]["stage4"] = 'OK'
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm4_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm4_mass"
    match = re.search(r'\d+$', key)
    if match:
        place_id = match.group()
    print(storage.get_arm_id(place_id, user["location_id"]))
    apm4_data["arm_id"] = storage.get_arm_id(place_id, user["location_id"])
    apm4_data["title"] = ui_welcome_mode[key]
    text = f'{apm4_data["title"]}:\n{apm4_text_action}'
    keyboard = tgm.make_inline_keyboard(apm4_cancel)
    return text, keyboard

welcome_handlers["kbd_mode_apm4_mass"] = apm4_done_hndl