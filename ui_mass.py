from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage
from datetime import datetime
import pytz

mass_text_entry = "Введите массу животного в граммах"
mass_text_incorrect = "Неверный ввод:"

GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y")
GET_HISTORY = lambda user, entry: f'{GET_NOW()}({user["id"]}): {ui_welcome_mode["kbd_mass"]} - {entry}'

mass_cancel = {
    "kbd_cancel":"Отмена",
}

def mass_entry_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)
    if not msg.isdigit():
        text = f'{ui_welcome_mode["kbd_mass"]}:\n{mass_text_incorrect} {msg}\n'
        text += mass_text_entry
        keyboard = tgm.make_inline_keyboard(mass_cancel)
        return text, keyboard

    bird["mass"] = msg

    # todo need saving to SQL
    if not "history" in bird:
        bird["history"] = []
    text = f'Масса животного {msg} гр.'
    bird["history"].append(GET_HISTORY(user, text))
    return ui_welcome(user)


############################################
# Global API
############################################
def ui_mass_entry_mode(user, key=None, msg=None)->(str,):
    if not storage.get_bird(user["code"]):
        return ui_welcome(user)
    user["mode"] = "kbd_mode_mass_entry"
    text = f'{ui_welcome_mode["kbd_mass"]}:\n{mass_text_entry}'
    keyboard = tgm.make_inline_keyboard(mass_cancel)
    return text, keyboard

welcome_handlers["kbd_mode_mass_entry"] = mass_entry_hndl