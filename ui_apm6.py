from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage

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

def apm6_sex_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)
    bird["sex"] = kbd_apm6_sex[key]
    user["mode"] = "mode_apm6_species"

    text = f'{ui_welcome_mode["kbd_mode_apm6"]}:\n{apm6_text_species}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard
    
def apm6_species_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)
    bird["species"] = msg
    user["mode"] = "mode_apm6_clinic"

    text = f'{ui_welcome_mode["kbd_mode_apm6"]}:\n{apm6_text_clinic_state}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard

def apm6_done_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if bird:
        bird["clinic_state"] = msg
        bird["stage6"] = 'OK'
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm6_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm6_sex"
    text = f'{ui_welcome_mode["kbd_mode_apm6"]}:\n{apm6_text_sex}'
    keyboard = tgm.make_inline_keyboard(kbd_apm6_sex)
    return text, keyboard

welcome_handlers["kbd_mode_apm6_sex"] = apm6_sex_hndl
welcome_handlers["mode_apm6_species"] = apm6_species_hndl
welcome_handlers["mode_apm6_clinic"] = apm6_done_hndl

welcome_handlers["kbd_male"] = apm6_sex_hndl
welcome_handlers["kbd_female"] = apm6_sex_hndl