from ui_welcome import welcome_handlers, ui_welcome_mode, ui_welcome
import tgm
from storage import storage
from datetime import datetime

datetime_format = "%H:%M"
date_format = "%d.%m.%y"

apm5_text_action = "Выполните необходимые операции и нажмите 'Готово'"

apm5_done = {
    "kbd_apm5_done": "Готово",
}

apm5_data = {
    "arm_id": None,
    "title": None,
    "place_id": 3,
    "manipulations": [],
    "manipulations_menu": {},
}

def apm5_done_hndl(user, key=None, msg=None) -> (str,):
    if "bird" in user:
        user["bird"]["stage5"] = "OK"
        
    return ui_welcome(user)


############################################
# Global API
############################################
def ui_apm5_mode(user, key=None, msg=None) -> (str,):
    user["mode"] = "kbd_mode_apm5"

    # Инициализируем arm    
    apm5_data["arm_id"] = storage.get_arm_id(apm5_data["place_id"], user["location_id"])
    apm5_data["title"] = ui_welcome_mode[key]

    animal_id = storage.get_animal_id(user["bird"]["bar_code"])
    text = f'{apm5_data["title"]}:\n\n{manipulation_history_text(animal_id)}\n\n{apm5_text_action}'

    # Динамически обновляем кнопкоменюшку манипуляций по доступным манипуляциям
    apm5_data["manipulations"] = storage.get_manipulations(apm5_data["place_id"])
    kbd_manip_prefix = "kbd_apm5_manip_"
    manipulations_menu = apm5_data['manipulations_menu'] = apm5_done.copy()
    for button in manipulations_menu:
        # Дефолтное меню манипуляций — все ведет на Done.
        welcome_handlers[button] = apm5_done_hndl

    for mannum, manip in enumerate(apm5_data["manipulations"]):
        button_code = f'''{kbd_manip_prefix}_{mannum}'''
        apm5_data['manipulations_menu'][button_code]=f'''{manip['name']}'''
        # Обновляем глобальные идентификаторы кнопок манипуляций.
        welcome_handlers[button_code] = apm5_manipulations_hndl

    keyboard = tgm.make_inline_keyboard(manipulations_menu)
    return text, keyboard


def manipulation_history_text(animal_id) -> (str,):
    history = sorted(storage.get_animal_history(animal_id), key=lambda item: item['datetime'])
    result_string = ""
    current_date = None
    for item in history:
        formatted_date = item['datetime'].strftime(date_format)
        if current_date != formatted_date:
            if current_date is not None:
                result_string += "\n"
            result_string += f"{formatted_date}\n"
        current_date = formatted_date
        result_string += f"{item['datetime'].strftime(datetime_format)} - {item['manipulation_name']} - {item['tg_nickname']}\n"
    return result_string.strip()            

def apm5_manipulations_hndl(user, key=None, msg=None)->(str,):
    if 'done' in key:
        # Завершаем, запомним, где и кто работал с птицей.
        storage.insert_place_history(apm5_data["arm_id"], user["bird"]["bar_code"], user["id"])
        return ui_welcome(user)

    manip = key.split('__')[1]  
    manip_num = int(manip)  
    manipulation = apm5_data["manipulations"][manip_num]
    animal_id = storage.get_animal_id(user["bird"]["bar_code"])
    storage.insert_history(manipulation["id"], animal_id, apm5_data["arm_id"], user["id"])

    text = f'{apm5_data["title"]}\n\n{manipulation_history_text(animal_id)}\n\n{apm5_text_action}'
    keyboard = tgm.make_inline_keyboard(apm5_data['manipulations_menu'])
    return text, keyboard


welcome_handlers["kbd_apm5_done"] = apm5_done_hndl