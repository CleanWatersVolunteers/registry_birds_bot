from ui_welcome import ui_welcome_get_card, welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage
from datetime import datetime

history_cancel = {
    "kbd_cancel":"Меню",
}

############################################
# Global API
############################################
def ui_history_mode(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)

    text = ui_welcome_get_card(user, bird)
    keyboard = tgm.make_inline_keyboard(history_cancel)

    animal_id = storage.get_animal_id(user["code"])
    if animal_id is not None:
        numerical_history = storage.get_animal_numerical_history(animal_id)
        history = storage.get_animal_history(animal_id)

    result_string = ""
    combined_history = numerical_history + history
    sorted_history = sorted(combined_history, key=lambda item: item['datetime'])

    # Формируем строку результата
    for item in sorted_history:
        formatted_date = item['datetime'].strftime("%H:%M %d.%m.%y")
        if 'type_name' in item:  # Проверяем, что это элемент из numerical_history
            result_string += f"{formatted_date} - {item['type_name']}: {item['value']} {item['type_units']} \n"
        else:  # Это элемент из history
            result_string += f"{formatted_date} - {item['manipulation_name']}\n"
    text += result_string.strip()
    if "history" in bird:
        for item in bird["history"]:
            print(item)
            text += f'{item}\n'
    return text, keyboard