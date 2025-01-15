from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage

apm3_text_action = "Выполните мойку животного и нажмите 'Готово'"

apm3_done = {
    "kbd_apm3_done":"Готово",
    "kbd_cancel":"Отмена",
}

def apm3_done_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if bird:
        bird["stage3"] = 'OK'
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm3_mode(user, key=None, msg=None)->(str,):
    if not storage.get_bird(user["code"]):
        return ui_welcome(user)
    user["mode"] = "kbd_mode_apm3"
    text = f'{ui_welcome_mode["kbd_mode_apm3"]}:\n{apm3_text_action}'
    keyboard = tgm.make_inline_keyboard(apm3_done)
    return text, keyboard

welcome_handlers["kbd_apm3_done"] = apm3_done_hndl