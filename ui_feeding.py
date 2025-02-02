from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from datetime import datetime
import pytz
from storage import storage

GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y")
GET_HISTORY = lambda user, entry: f'{GET_NOW()}({user["id"]}): {ui_welcome_mode["kbd_feeding"]} - {entry}'

feeding_text_sel_action = 'Выберите действие'
feeding_text_entry_fish = 'Введите количество съеденных рыб'
feeding_text_incorrect = "Неверный ввод:"

#todo Кормление - загружать идентификаторы и названия манипуляций из базы #50
feeding_actions = {
    "kbd_feeding_eat":"Ел сам",
    "kbd_feeding_not_eat":"Отказ от еды",
    "kbd_feeding_drink":"Пил сам",
    "kbd_feeding_not_drink":"Отказ от питья",
    "kbd_cancel":"Отмена",
}
feeding_cancel = {
    "kbd_cancel":"Отмена",
}
def feeding_action_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)
    if key == 'kbd_feeding_eat':
        user["mode"] = "kbd_feeding_entry_fish"
        text = f'{ui_welcome_mode["kbd_feeding"]}:\n{feeding_text_entry_fish}'
        keyboard = tgm.make_inline_keyboard(feeding_cancel)
        return text, keyboard

    animal_id = storage.get_animal_id(user["bird"]["bar_code"])
    if animal_id is not None:
        manipulation = {
            "animal_id": animal_id,
            "id" : None,
            "arms_id": 7,
            "tg_nickname": user["id"]
        }
        #todo Кормление - загружать идентификаторы и названия манипуляций из базы #50
        if key == 'kbd_feeding_drink': #2
            manipulation["id"] = 2
        elif key == 'kbd_feeding_not_eat': #3
            manipulation["id"] = 3        
        elif key == 'kbd_feeding_not_drink': #4
            manipulation["id"] = 4
        else:
            return ui_welcome(user)
        storage.insert_history(manipulation["id"], manipulation["animal_id"], manipulation["arms_id"], manipulation["tg_nickname"])
    return ui_welcome(user)

def feeding_entry_fish_hndl(user, key=None, msg=None)->(str,):
    if not "bird" in user:
        return ui_welcome(user)
    if not msg.isdigit():
        text = f'{ui_welcome_mode["kbd_feeding"]}:\n{feeding_text_incorrect} {msg}\n'
        text += feeding_text_entry_fish
        keyboard = tgm.make_inline_keyboard(feeding_cancel)
        return text, keyboard

    animal_id = storage.get_animal_id(user["bird"]["bar_code"])
    if animal_id is not None:
        manipulation = {
            "animal_id": animal_id,
            "id" : 1, #todo Кормление - загружать идентификаторы и названия манипуляций из базы #50
            "arms_id": 7,
            "tg_nickname": user["id"]
        }
        storage.insert_numerical_history(manipulation["animal_id"], manipulation["id"], int(msg), manipulation["tg_nickname"])
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_feeding_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_feeding"
    text = f'{ui_welcome_mode["kbd_feeding"]}:\n{feeding_text_sel_action}'
    keyboard = tgm.make_inline_keyboard(feeding_actions)
    return text, keyboard

welcome_handlers["kbd_feeding_eat"] = feeding_action_hndl
welcome_handlers["kbd_feeding_not_eat"] = feeding_action_hndl
welcome_handlers["kbd_feeding_drink"] = feeding_action_hndl
welcome_handlers["kbd_feeding_not_drink"] = feeding_action_hndl
welcome_handlers["kbd_feeding_entry_fish"] = feeding_entry_fish_hndl