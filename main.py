import asyncio
from telegram import InlineKeyboardButton, Update, constants
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from logs import log

from ui_welcome import *



from database import Database as db
from ui.entry import entry_start, entry_button


f = open('token', 'r')
TELEGRAM_BOT_TOKEN = f.read()
f.close()

# log.init("logs.txt") 					# todo remove it
# storage.init("user.base","birds.base")  # todo remove it


db.init()


def kbd_to_inline(text_list):
	keyboard = []
	for key in text_list:
		keyboard.append([InlineKeyboardButton(key, callback_data=text_list[key])])
	return keyboard

async def cb_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	text, keyboard = entry_start(update['message']['from']['username'], update['message']['text'])
	try:
		if keyboard:
			await update.message.reply_text(text, 
				parse_mode=constants.ParseMode.MARKDOWN_V2, 
				reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
			)
		else:
			await update.message.reply_text(text, parse_mode=constants.ParseMode.MARKDOWN_V2)
	except Exception as e:
		print('[!!] Exception ', e)

async def cb_user_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	query = update.callback_query
	await query.answer()

	username = query.from_user.username
	button = query.data.split('_')[0]

	text, keyboard = entry_button(username, query.message.text, query.data)
	try:
		if keyboard:
			await query.edit_message_text(text=text, 
				parse_mode=constants.ParseMode.MARKDOWN_V2, 
				reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
			)
		else:
			await query.message.reply_text(text=text, 
				parse_mode=constants.ParseMode.MARKDOWN_V2
			)
		
	except Exception as e:
		print('[!!] Exception ', e)




    # user = user_get_create(username)
    # if not user:
    #     print("[!!] Ошибка пользователя!", username)
    #     text = "Ошибка\!"
    #     await query.edit_message_text(text=text_escape(text), parse_mode=text_parse_mode)
    #     return None

    # # show menu
    # if query.data in kbd_handlers_list.keys():
    #     text, keyboard = kbd_handlers_list[query.data](user=user, key=query.data, message=query.message.text)
    # else:
    #     print(f"[!!] Got unexpected argument: {query.data}")
    #     text = "Ошибка\!"
    #     keyboard = None

    # try:
    #     if keyboard:
    #         await query.edit_message_text(text=text_escape(text), parse_mode=text_parse_mode, reply_markup=InlineKeyboardMarkup(keyboard))

    # return None


async def main() -> None:
	application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

	application.add_handler(CommandHandler("start", cb_user_message))
	application.add_handler(MessageHandler(filters.TEXT, cb_user_message))
	# application.add_handler(MessageHandler(filters.PHOTO, tg_user_photo))

	application.add_handler(CallbackQueryHandler(cb_user_button))

	await application.initialize()
	await application.start()
	await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

	log.logi("Bot 'Registry Birds v1.0.0' enabled")

	while True:
		await asyncio.sleep(5*60)

	await application.updater.stop()
	log.logi("Bot disabled")

	await application.shutdown()


if __name__ == "__main__":
	asyncio.run(main())

