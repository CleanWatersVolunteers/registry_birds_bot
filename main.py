import asyncio
from telegram import InlineKeyboardButton, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from logs import log

from ui_welcome import *



from database import Database as db
from ui.entry import entry_start, entry_button, entry_photo


f = open('token', 'r')
TELEGRAM_BOT_TOKEN = f.read()
f.close()

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
				reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
			)
		else:
			await update.message.reply_text(text)
	except Exception as e:
		print('[!!] Exception ', e)

async def cb_user_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	query = update.callback_query
	await query.answer()

	username = query.from_user.username
	text, keyboard = entry_button(username, query.message.text, query.data)
	try:
		if keyboard:
			await query.edit_message_text(text=text, 
				reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
			)
		else:
			await query.message.reply_text(text=text)
		
	except Exception as e:
		print('[!!] Exception ', e)

async def cb_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	username = update["message"]["from"]["username"]

	new_file = await update.message.effective_attachment[-1].get_file()
	data = await new_file.download_as_bytearray()
	text, keyboard = entry_photo(username, data)
	try:
		if keyboard:
			await update.message.reply_text(text=text,
				reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
			)
		else:
			await update.message.reply_text(text=text)
		
	except Exception as e:
		print('[!!] Exception ', e)


async def main() -> None:
	application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

	application.add_handler(CommandHandler("start", cb_user_message))
	application.add_handler(MessageHandler(filters.TEXT, cb_user_message))
	application.add_handler(MessageHandler(filters.PHOTO, cb_user_photo))

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

