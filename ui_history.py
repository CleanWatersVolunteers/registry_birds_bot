from ui_welcome import ui_welcome_get_card, ui_welcome
import tgm
from storage import storage

history_cancel = {
    "kbd_cancel":"Меню",
}

manipulations_not_found = "Манипуляции не найдены"

############################################
# Global API
############################################
def ui_history_mode(user, key=None, msg=None)->(str,):
    bird = user["bird"]
    if not bird:
        return ui_welcome(user)

    text = ui_welcome_get_card(bird["bar_code"])
    keyboard = tgm.make_inline_keyboard(history_cancel)

    animal_id = storage.get_animal_id(bird["bar_code"])
    numerical_history = ""
    history = ""

    if animal_id is not None:
        numerical_history = storage.get_animal_numerical_history(animal_id)
        history = storage.get_animal_history(animal_id)
        place_history = storage.get_place_history(animal_id)

    combined_history = numerical_history + history + place_history
    sorted_history = sorted(combined_history, key=lambda item: item['datetime'])
    result_string = ""
    current_date = None
    for item in sorted_history:
        formatted_date = item['datetime'].strftime("%d.%m.%y")
        if current_date != formatted_date:
            if current_date is not None:
                result_string += "\n"
            result_string += f"{formatted_date}\n"
            current_date = formatted_date
        if 'type_name' in item:  # Элемент из numerical_history
            result_string += f"{item['datetime'].strftime('%H:%M')} - {item['type_name']}: {item['value']} {item['type_units']} - {item['tg_nickname']}\n"
        elif 'manipulation_name' in item:  # Элемент из history
            result_string += f"{item['datetime'].strftime('%H:%M')} - {item['manipulation_name']} - {item['tg_nickname']}\n"
        else:
            result_string += f"{item['datetime'].strftime('%H:%M')} - {item['place_name']} - {item['location_name']}\n"
    if result_string == "":
        text += manipulations_not_found
    else:
        text += result_string.strip()
    return text, keyboard