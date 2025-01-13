from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


def get_username_in_text(): 
    pass
def get_username_in_query(query):
    pass

def make_inline_keyboard(text_list):
    keyboard = []
    for item in text_list:
        keyboard.append([InlineKeyboardButton(text_list[item], callback_data=item)])
    return keyboard

# def make_inline_keyboard(text_list):
#     line_text_len = 0
#     keyboard = []
#     kb_line = []
#     # sorted_keys = sorted(text_list.keys())
#     sorted_keys = text_list.keys()
#     # print(text_list.keys(), sorted_keys)
#     for item in sorted_keys:
#         if line_text_len + len(text_list[item]) > 30:
#             keyboard.append(kb_line)
#             kb_line = []
#             line_text_len = 0
#         kb_line.append(
#             InlineKeyboardButton(text_list[item], callback_data=item)
#         )
#         line_text_len += len(text_list[item])
#     keyboard.append(kb_line)
#     # print(keyboard)
#     return keyboard