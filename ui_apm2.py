from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm
from storage import storage

apm2_text_action = "Выполните необходимые операции и нажмите 'Готово'"

apm2_done = {
    "kbd_apm2_done":"Готово",
    "kbd_cancel":"Отмена",
}

def apm2_done_hndl(user, key=None, msg=None)->(str,):
    if "bird" in user:
        user["bird"]["stage2"] = "OK"
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm2_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm2"
    arm_code = 2
    manipulations = storage.get_manipulations(arm_code)
    text = f'{ui_welcome_mode["kbd_mode_apm2"]}:\n'
    for manipulation in manipulations:
        text += manipulation['name'] + '\n'
    text += apm2_text_action
    keyboard = tgm.make_inline_keyboard(apm2_done)
    return text, keyboard

welcome_handlers["kbd_apm2_done"] = apm2_done_hndl