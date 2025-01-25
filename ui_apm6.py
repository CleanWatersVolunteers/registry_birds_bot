from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage
import re

apm6_text_sex = "Выберите пол животного"
apm6_text_species = "Введите вид животного"
apm6_text_clinic_state = "Введите клиническое состояние"

kbd_apm6_sex = {
    "kbd_male":"муж",
    "kbd_female":"жен",
    "kbd_cancel":"Отмена",
}
apm6_cancel = {
    "kbd_cancel":"Отмена",
}

data = {
    "arm_id": None,
    "title": None
}

def apm6_sex_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)
    if kbd_apm6_sex[key] == kbd_apm6_sex["kbd_female"]:
        storage.update_animal(user["bird"]["bar_code"], female=True)
    else:
        storage.update_animal(user["bird"]["bar_code"], female=False)
    user["mode"] = "mode_apm6_species"
    text = f'{data["title"]}:\n{apm6_text_species}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard
    
def apm6_species_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)
    storage.update_animal(user["bird"]["bar_code"], species = msg)
    user["mode"] = "mode_apm6_clinic"
    text = f'{data["title"]}:\n{apm6_text_clinic_state}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard

def apm6_done_hndl(user, key=None, msg=None)->(str,):
    if "bird" in user:
        storage.update_animal(user["bird"]["bar_code"], clinical_condition_admission = msg)
        user["bird"]["stage6"] = 'OK'
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm6_mode(user, key=None, msg=None)->(str,):
    match = re.search(r'\d+$', key)
    if match:
        data["arm_id"] = int(match.group())
    data["title"] = ui_welcome_mode[key]
    user["mode"] = "kbd_mode_apm6_sex"
    text = f'{data["title"]}:\n{apm6_text_sex}'
    keyboard = tgm.make_inline_keyboard(kbd_apm6_sex)
    return text, keyboard

welcome_handlers["kbd_mode_apm6_sex"] = apm6_sex_hndl
welcome_handlers["mode_apm6_species"] = apm6_species_hndl
welcome_handlers["mode_apm6_clinic"] = apm6_done_hndl

welcome_handlers["kbd_male"] = apm6_sex_hndl
welcome_handlers["kbd_female"] = apm6_sex_hndl