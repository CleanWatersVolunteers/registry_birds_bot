from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage

apm0_text_entry_barode = f'Введите баркод или загрузите фото'
apm0_text_incorrect_barode = f'Неверный ввод: '
apm0_text_check_barode = 'Получен баркод:'
apm0_text_bird_found = 'Птица найдена:'
apm0_text_bird_not_found = 'Птица не найдена:'

APM0_TEXT = lambda text: f'{ui_welcome_mode["kbd_mode_apm0"]}:\n{text}'


apm0_done = {
    "kbd_apm0_done":"Готово",
    "kbd_cancel":"Отмена",
}
apm0_sw_bird = {
    "kbd_apm0_sw_bird":"Готово",
    "kbd_cancel":"Отмена",
}

apm0_cancel = {
    "kbd_cancel":"Отмена",
}

def apm0_done_hndl(user, key=None, msg=None)->(str,):
    # print(user, key, msg)
    barcode = msg.split(':')[-1]

    if key == "kbd_apm0_done":
        print(f'[..] New bird with barcode {barcode}')
        storage.add_bird(barcode)
    else:
        print(f'[..] Selected bird with barcode {barcode}')
    user["code"] = barcode
    return ui_welcome(user)

############################################
# Global API
############################################
# create new bird
def apm0_add_bird(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_mode_apm0"
    text = APM0_TEXT(apm0_text_entry_barode) 
    keyboard = tgm.make_inline_keyboard(apm0_cancel)
    return text, keyboard

# find existing bird
def apm0_sel_bird(user, key=None, msg=None)->(str,):
    print(msg)
    user["mode"] = "kbd_mode_apm0_sw"
    text = APM0_TEXT(apm0_text_entry_barode) 
    keyboard = tgm.make_inline_keyboard(apm0_cancel)
    return text, keyboard

# barcode parser
def apm0_entry(user, key=None, msg=None)->(str,):
    print(f'[..] Entered barcode {msg}')
    barcode = msg

    if not barcode.isdigit():
        text = APM0_TEXT(apm0_text_incorrect_barode) 
        text += f'{barcode}\n'
        text += apm0_text_entry_barode
        keyboard = tgm.make_inline_keyboard(apm0_cancel)
        return text, keyboard

    text = APM0_TEXT(apm0_text_check_barode) 
    text += barcode
    if user["mode"] == "kbd_mode_apm0": # new bird
        keyboard = tgm.make_inline_keyboard(apm0_done)
        if storage.get_bird(barcode):
            text = APM0_TEXT(apm0_text_bird_found) 
            text += barcode
            keyboard = tgm.make_inline_keyboard(apm0_sw_bird)
    else:   # find bird
        if storage.get_bird(barcode):
            text = APM0_TEXT(apm0_text_bird_found) 
            text += barcode
            keyboard = tgm.make_inline_keyboard(apm0_sw_bird)
        else:
            text = APM0_TEXT(apm0_text_bird_not_found) 
            keyboard = tgm.make_inline_keyboard(apm0_cancel)
            text += f'{barcode}\n'
            text += apm0_text_entry_barode
    return text, keyboard


welcome_handlers["kbd_mode_apm0"] = apm0_entry
welcome_handlers["kbd_mode_apm0_sw"] = apm0_entry
welcome_handlers["kbd_add_bird"] = apm0_add_bird
welcome_handlers["kbd_sel_bird"] = apm0_sel_bird

welcome_handlers["kbd_apm0_done"] = apm0_done_hndl
welcome_handlers["kbd_apm0_sw_bird"] = apm0_done_hndl