from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage

apm5_text_action = "Выполните необходимые операции и нажмите 'Готово'"

apm5_done = {
    "kbd_apm5_done":"Готово",
    "kbd_cancel":"Отмена",
}

def apm5_done_hndl(user, key=None, msg=None)->(str,):
    if "bird" in user:
        user["bird"]["stage5"] = "OK"
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm5_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm5"
    text = f'{ui_welcome_mode["kbd_mode_apm5"]}:\n{apm5_text_action}'
    keyboard = tgm.make_inline_keyboard(apm5_done)
    return text, keyboard

welcome_handlers["kbd_apm5_done"] = apm5_done_hndl