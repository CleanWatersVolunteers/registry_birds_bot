from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage
import re
from datetime import datetime

apm6_text_species = "Введите вид животного"
apm6_text_clinic_state = "Введите клиническое состояние"

apm6_cancel = {
    "kbd_cancel":"Отмена",
}

apm6_data = {
    "arm_id": None,
    "title": None,
    "place_id": 3,
}

apm6_text_manipulations = "Проведем манипуляции?"

manipulations = storage.get_manipulations(apm6_data["place_id"])

# Заполняем кнопкоменюшку манипуляций
# глобальный префикс для кнопок доступных манипуляций
kbd_manip_prefix = 'kbd_apm6_manip_'
apm6_manipulations = {
    f"{kbd_manip_prefix}_cancel": "Больше ничего не надо",
}
for mannum, manip in enumerate(manipulations):
    button_code = f'''{kbd_manip_prefix}_{mannum}'''
    apm6_manipulations[button_code]=f'''{manip['name']}'''


def apm6_species_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)
    storage.update_animal(user["bird"]["bar_code"], species = msg)
    user["mode"] = "mode_apm6_clinic"
    text = f'{apm6_data["title"]}:\n{apm6_text_clinic_state}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard


def apm6_clinical_condition_hndl(user, key=None, msg=None)->(str,):
    if "bird" in user:
        storage.update_animal(user["bird"]["bar_code"], clinical_condition_admission = msg)
        user["bird"]["stage6"] = 'OK'
    user["mode"] = "mode_apm6_manipulations"

    # Манипуляции всегда могут изменится, тут бы надо их обновлять, 
    # но придется еще и хандлеры кнопок обновлять, могут быть риски с архитектурой, не очень понятно, как сделать это правильно.
    # поэтому пока не обновляем, после правки списка манипуляций нужно перезапускать бот

    text = f'{apm6_data["title"]}:\n{apm6_text_manipulations}'
    keyboard = tgm.make_inline_keyboard(apm6_manipulations)

    return text, keyboard

def apm6_manipulations_hndl(user, key=None, msg=None)->(str,):
    manip = key.split('__')[1]  
    if manip == 'cancel':
        # Завершаем, запомним, где и кто работал с птицей.
        storage.insert_place_history(apm6_data["arm_id"], user["bird"]["bar_code"], user["id"])
        return ui_welcome(user)

    manip_num = int(manip)  
    manipulation = manipulations[manip_num]
    animal_id = storage.get_animal_id(user["bird"]["bar_code"])
    storage.insert_history(manipulation["id"], animal_id, apm6_data["arm_id"], user["id"])

    hhmmss = datetime.now().strftime("%H:%M:%S")
    manip_feedback = f'''Записали «{hhmmss}: {manipulation['name']}»'''

    text = f'{apm6_data["title"]} → {manip_feedback}. Нужно еще? \n{apm6_text_manipulations}'
    keyboard = tgm.make_inline_keyboard(apm6_manipulations)
    return text, keyboard


############################################
# Global API
############################################
def ui_apm6_mode(user, key=None, msg=None)->(str,):
    match = re.search(r'\d+$', key)
    if match:
        apm6_data["arm_id"] = int(match.group())
    apm6_data["title"] = ui_welcome_mode[key]
    user["mode"] = "mode_apm6_species"
    text = f'{apm6_data["title"]}:\n{apm6_text_species}'
    keyboard = tgm.make_inline_keyboard(apm6_cancel)
    return text, keyboard

welcome_handlers["mode_apm6_species"] = apm6_species_hndl
welcome_handlers["mode_apm6_clinic"] = apm6_clinical_condition_hndl
welcome_handlers["mode_apm6_manipulations"] = apm6_manipulations_hndl

# Загружаем в глобальные идентификаторы кнопок манипуляций.
for button in apm6_manipulations:
    welcome_handlers[button] = apm6_manipulations_hndl
