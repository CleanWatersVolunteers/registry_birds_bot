from ui_welcome import ui_welcome_get_card, welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage

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

    if "history" in bird:
        for item in bird["history"]:
            print(item)
            text += f'{item}\n'
    return text, keyboard
