from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage

apm4_text_action = "Введите массу животного в граммах"
apm4_text_incorrect = "Неверный ввод:"

apm4_cancel = {
    "kbd_cancel":"Отмена",
}

def apm4_done_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)
    if not msg.isdigit():
        text = f'{ui_welcome_mode["kbd_mode_apm4"]}:\n{apm4_text_incorrect} {msg}\n'
        text += apm4_text_action
        keyboard = tgm.make_inline_keyboard(apm4_cancel)
        return text, keyboard

    user["mode"] = None
    bird["mass"] = msg
    bird["stage4"] = 'OK'
    storage.insert_place_history(user["code"], user["id"])
    storage.set_animal_weight(user["code"], msg)
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm4_mode(user, key=None, msg=None)->(str,):
    if not storage.get_bird(user["code"]):
        return ui_welcome(user)
    user["mode"] = "kbd_mode_apm4_mass"
    text = f'{ui_welcome_mode["kbd_mode_apm4"]}:\n{apm4_text_action}'
    keyboard = tgm.make_inline_keyboard(apm4_cancel)
    return text, keyboard

welcome_handlers["kbd_mode_apm4_mass"] = apm4_done_hndl