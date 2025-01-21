from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage

apm4_text_action = "Введите массу животного в граммах"
apm4_text_incorrect = "Неверный ввод:"

apm4_cancel = {
    "kbd_cancel":"Отмена",
}

def apm4_done_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)
    if not msg.isdigit():
        text = f'{ui_welcome_mode["kbd_mode_apm4"]}:\n{apm4_text_incorrect} {msg}\n'
        text += apm4_text_action
        keyboard = tgm.make_inline_keyboard(apm4_cancel)
        return text, keyboard

    user["mode"] = None
    user["bird"]["mass"] = msg
    user["bird"]["stage4"] = 'OK'
    storage.insert_place_history(user["bird"]["bar_code"], user["id"])
    storage.update_animal(user["bird"]["bar_code"], weight = msg)
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm4_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm4_mass"
    text = f'{ui_welcome_mode["kbd_mode_apm4"]}:\n{apm4_text_action}'
    keyboard = tgm.make_inline_keyboard(apm4_cancel)
    return text, keyboard

welcome_handlers["kbd_mode_apm4_mass"] = apm4_done_hndl