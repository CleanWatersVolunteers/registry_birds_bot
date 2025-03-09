from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
import tgm
from storage import storage

lb_text_entry_barode = f'Введите баркод или загрузите фото с одним баркодом'
lb_text_incorrect_barode = f'Неверный ввод:'
lb_text_check_barode = 'Получен баркод:'
lb_text_bird_found = 'Птица найдена:'
lb_text_bird_not_found = 'Птица не найдена:'

LB_TEXT = lambda label, text: f'{label}:\n{text}'

lb_done = {
    "kbd_load_bird_done":"Готово",
    "kbd_cancel":"Отмена",
}
lb_sw_bird = {
    "kbd_load_bird_sw":"Готово",
    "kbd_cancel":"Отмена",
}

lb_cancel = {
    "kbd_cancel":"Отмена",
}

def ui_load_bird_done_hndl(user, key=None, msg=None)->(str,):
    # print(user, key, msg)
    barcode = msg.split(':')[-1]

    if key == "kbd_load_bird_done":
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
def ui_load_bird_add(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_barcode_add"
    text = LB_TEXT(ui_welcome_mode["kbd_add_bird"], lb_text_entry_barode) 
    keyboard = tgm.make_inline_keyboard(lb_cancel)
    return text, keyboard

# find existing bird
def ui_load_bird_sel(user, key=None, msg=None)->(str,):
    user["mode"] = "kbd_barcode_sel"
    text = LB_TEXT(ui_welcome_mode["kbd_sel_bird"],lb_text_entry_barode) 
    keyboard = tgm.make_inline_keyboard(lb_cancel)
    return text, keyboard

# barcode parser
def ui_load_bird_barcode(user, key=None, msg=None)->(str,):
    print(f'[..] Entered barcode {msg}')
    barcode = msg
    if user["mode"] == "kbd_barcode_add":
        text = f'{ui_welcome_mode["kbd_add_bird"]}\n'
    else:
        text = f'{ui_welcome_mode["kbd_sel_bird"]}\n'

    if not barcode.isdigit():
        text += lb_text_incorrect_barode
        text += f'{barcode}\n'
        text += lb_text_entry_barode
        keyboard = tgm.make_inline_keyboard(lb_cancel)
        return text, keyboard

    bird = storage.get_bird(barcode)
    if bird:
        text = lb_text_bird_found
        text += f'{barcode}'
        keyboard = tgm.make_inline_keyboard(lb_done)
        return text, keyboard

    if user["mode"] == "kbd_barcode_add":
        text += lb_text_check_barode
        text += barcode
        keyboard = tgm.make_inline_keyboard(lb_done)
    else:
        text = lb_text_bird_not_found
        text += f'{barcode}'
        keyboard = tgm.make_inline_keyboard(lb_cancel)
    return text, keyboard

welcome_handlers["kbd_barcode_add"] = ui_load_bird_barcode
welcome_handlers["kbd_barcode_sel"] = ui_load_bird_barcode
welcome_handlers["kbd_load_bird_done"] = ui_load_bird_done_hndl
welcome_handlers["kbd_load_bird_sw"] = ui_load_bird_done_hndl

