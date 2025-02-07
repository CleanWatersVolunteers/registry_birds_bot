from ui_welcome import welcome_handlers, ui_welcome_mode, ui_welcome
import tgm
from storage import storage
import re

apm2_text_action = "Выполните необходимые манипуляции и нажмите 'Готово'"
apm2_text_animal_header = "Животное №:"

apm2_done = {
    "kbd_apm2_done": "Готово",
    "kbd_cancel": "Отмена",
}

def apm2_done_hndl(user, key=None, msg=None) -> (str,):
   return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm2_mode(user, key=None, msg=None) -> (str,):
    user["mode"] = "kbd_mode_apm2"
    match = re.search(r'\d+$', key)
    if match:
        storage.insert_place_history(int(match.group()), user["bird"]["animal_id"], user["id"])
    text = f'{ui_welcome_mode[key]}\n'
    text += f'{apm2_text_animal_header}{user["bird"]["bar_code"]}\n'
    text += apm2_text_action
    keyboard = tgm.make_inline_keyboard(apm2_done)
    return text, keyboard

welcome_handlers["kbd_apm2_done"] = apm2_done_hndl