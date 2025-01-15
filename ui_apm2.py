from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage

apm2_text_action = "Выполните необходимые операции и нажмите 'Готово'"

apm2_done = {
    "kbd_apm2_done":"Готово",
    "kbd_cancel":"Отмена",
}

def apm2_done_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if bird:
        bird["stage2"] = 'OK'
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm2_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm2"
    text = f'{ui_welcome_mode["kbd_mode_apm2"]}:\n{apm2_text_action}'
    keyboard = tgm.make_inline_keyboard(apm2_done)
    return text, keyboard

welcome_handlers["kbd_apm2_done"] = apm2_done_hndl