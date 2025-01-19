from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from datetime import datetime
import pytz
from storage import storage

GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y")
GET_HISTORY = lambda user, entry: f'{GET_NOW()}({user["id"]}): {ui_welcome_mode["kbd_feeding"]} - {entry}'

feeding_text_sel_action = 'Выберите действие'
feeding_text_entry_fish = 'Введите количество съеденных рыб'
feeding_text_incorrect = "Неверный ввод:"


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
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)
    if key == 'kbd_feeding_eat':
        user["mode"] = "kbd_feeding_entry_fish"
        text = f'{ui_welcome_mode["kbd_feeding"]}:\n{feeding_text_entry_fish}'
        keyboard = tgm.make_inline_keyboard(feeding_cancel)
        return text, keyboard

    # todo need saving to SQL
    if not "history" in bird:
        bird["history"] = []
    bird["history"].append(GET_HISTORY(user, feeding_actions[key]))
    return ui_welcome(user)

def feeding_entry_fish_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)
    if not msg.isdigit():
        text = f'{ui_welcome_mode["kbd_feeding"]}:\n{feeding_text_incorrect} {msg}\n'
        text += feeding_text_entry_fish
        keyboard = tgm.make_inline_keyboard(feeding_cancel)
        return text, keyboard

    # todo need saving to SQL
    if not "history" in bird:
        bird["history"] = []
    text = f'{feeding_actions["kbd_feeding_eat"]} {msg} рыб'
    bird["history"].append(GET_HISTORY(user, text))
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_feeding_mode(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        return ui_welcome(user)
    user["mode"] = "kbd_mode_feeding"
    text = f'{ui_welcome_mode["kbd_feeding"]}:\n{feeding_text_sel_action}'
    keyboard = tgm.make_inline_keyboard(feeding_actions)
    return text, keyboard

welcome_handlers["kbd_feeding_eat"] = feeding_action_hndl
welcome_handlers["kbd_feeding_not_eat"] = feeding_action_hndl
welcome_handlers["kbd_feeding_drink"] = feeding_action_hndl
welcome_handlers["kbd_feeding_not_drink"] = feeding_action_hndl
welcome_handlers["kbd_feeding_entry_fish"] = feeding_entry_fish_hndl