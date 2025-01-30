from ui_welcome import welcome_handlers, ui_welcome_mode, ui_welcome
import tgm
from storage import storage
import re

apm6_text_species = "Введите вид животного"
apm6_text_clinic_state = "Введите клиническое состояние"
apm6_text_animal_header = "Животное №:"

apm6_cancel = {
    "kbd_cancel": "Отмена",
}

apm6_data = {
    "arm_id": None,
    "title": None
}

def apm6_species_hndl(user, key=None, msg=None) -> (str,):
    if not "bird" in user:
        return ui_welcome(user)
    storage.update_animal(user["bird"]["bar_code"], species=msg)
    user["mode"] = "mode_apm6_clinic"
    text = f'{apm6_data["title"]}:\n{apm6_text_clinic_state}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard

def apm6_done_hndl(user, key=None, msg=None) -> (str,):
    if "bird" in user:
        storage.update_animal(user["bird"]["bar_code"], clinical_condition_admission=msg)
        user["bird"]["stage6"] = 'OK'
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm6_mode(user, key=None, msg=None) -> (str,):
    match = re.search(r'\d+$', key)
    if match:
        apm6_data["arm_id"] = int(match.group())
    apm6_data["title"] = ui_welcome_mode[key]
    user["mode"] = "mode_apm6_species"
    text = f'{apm6_data["title"]}:\n'
    text += f'{apm6_text_animal_header}{user["bird"]["bar_code"]}\n'
    text += f'{apm6_text_species}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard

welcome_handlers["mode_apm6_species"] = apm6_species_hndl
welcome_handlers["mode_apm6_clinic"] = apm6_done_hndl
