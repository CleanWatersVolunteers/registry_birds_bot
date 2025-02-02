from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome
import tgm

apm3_text_action = "Выполните мойку животного и нажмите 'Готово'"

apm3_done = {
    "kbd_apm3_done":"Готово",
    "kbd_cancel":"Отмена",
}

def apm3_done_hndl(user, key=None, msg=None)->(str,):
    if "bird" in user:
        user["bird"]["stage3"] = "OK"
    return ui_welcome(user)

############################################
# Global API
############################################
def ui_apm3_mode(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm3"
    text = f'{ui_welcome_mode[key]}:\n{apm3_text_action}'
    keyboard = tgm.make_inline_keyboard(apm3_done)
    return text, keyboard

welcome_handlers["kbd_apm3_done"] = apm3_done_hndl