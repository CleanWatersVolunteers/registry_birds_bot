from ui_apm2 import ui_apm2_mode
from ui_welcome import welcome_addr_hndl, welcome_handlers, ui_welcome
from ui_apm1 import ui_apm1_mode
import tgm
from storage import storage
from ui_welcome import welcome_sel_addr
from ui_apm1 import ui_apm1_mode

lb_text_header = 'Загрузка птицы:\n'
lb_text_entry_barode = f'Введите баркод или загрузите фото с баркодом\n(на фото должен быть только один баркод)'
lb_text_incorrect_barcode = f'Неверный ввод:'
lb_text_not_found = '\nЖивотное не найдено.'

lb_cancel = {
    "kbd_cancel": "Назад",
}

lb_ok = {
    "kbd_return_barcode_entry": "Ок",
}

############################################
# Global API
############################################
# create new bird
def ui_load_bird(user, key=None, msg=None):
    user["mode"] = "kbd_barcode_entry"
    text = f'{lb_text_header}{lb_text_entry_barode}'
    keyboard = tgm.make_inline_keyboard(lb_cancel)
    return text, keyboard

# barcode parser
def ui_load_bird_barcode(user, key=None, msg=None):
    print(f'[..] Entered barcode {msg}')
    barcode = msg
    text = lb_text_header
    if not barcode.isdigit():
        print(f'[!!] Barcode incorrect: \'{msg}\'')
        text += lb_text_incorrect_barcode
        text += f'{barcode}\n'
        text += lb_text_entry_barode
        keyboard = tgm.make_inline_keyboard(lb_cancel)
        return text, keyboard

    user["bird"] = storage.get_animal_by_bar_code(barcode)
    if user["bird"]:
        if user.get("apm") == 'kbd_mode_apm1':
            return ui_apm2_mode(user, msg=msg)
        else:
            return ui_welcome(user)
    print("[..] Bird not found")
    
    user["bird"] = {"bar_code": barcode}
    
    if user.get("apm"):
        return lb_text_not_found, tgm.make_inline_keyboard(lb_ok)
    else:    
        return ui_apm1_mode(user, key, msg)

def ui_cancel_load_bird(user, key=None, msg=None):
    return welcome_sel_addr(user)

welcome_handlers["kbd_cancel"] = ui_cancel_load_bird
welcome_handlers["kbd_barcode_entry"] = ui_load_bird_barcode
welcome_handlers["kbd_back_to_load_barcode"] = welcome_addr_hndl
welcome_handlers["kbd_return_barcode_entry"] = welcome_addr_hndl
