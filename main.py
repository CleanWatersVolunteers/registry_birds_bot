from dotenv import load_dotenv

load_dotenv()

import os
import asyncio
import re
from logs import my_logger

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

from database import Database as Db
from storage import QRCodeStorage
from ui.entry import entry_start, entry_button, entry_photo, SUPERVISOR_ARM
from ui.gen import (
	qr_cmd_gen24,
	qr_cmd_gen48,
	qr_cmd_gen72,
	qr_cmd_old,

	gen_pdf
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TEXT_QR_CODES_READY = "📄 Ваши QR-коды"
TEXT_QR_NOT_PREVIOUSLY_PRINTED = "❌ Этот код не был распечатан ранее. Повторите ввод."

SLEEP = 5 * 60

Db.init()


def kbd_to_inline(text_list):
	keyboard = []
	if isinstance(text_list, dict):
		for key in text_list:
			keyboard.append([InlineKeyboardButton(key, callback_data=text_list[key])])
	else:
		for text_line in text_list:
			line = []
			for btn in text_line:
				line.append(InlineKeyboardButton(callback_data=text_line[btn], text=btn))
			keyboard.append(line)
	return keyboard


async def cb_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	text, keyboard = entry_start(update['message']['from']['username'], update['message']['from']['id'],
								 update['message']['text'])
	try:
		if keyboard:
			await update.message.reply_text(text,
											reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
											)
		else:
			await update.message.reply_text(text)
	except Exception as e:
		my_logger.error('Exception cb_user_message ', e)


async def cb_user_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	query = update.callback_query
	await query.answer()

	username = query.from_user.username
	user_id = query.from_user.id
	my_logger.debug(f'cb_user_button username: {username}, user_id: {user_id}')
	text, keyboard = entry_button(username, user_id, query.message.text, query.data)
	try:
		if keyboard:
			await query.edit_message_text(text=text,
										  reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
										  )
		else:
			await query.message.reply_text(text=text)

	except Exception as e:
		my_logger.error('Exception cb_user_button ', e)


async def cb_user_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user_id = update["message"]["from"]["id"]
	new_file = await update.message.effective_attachment[-1].get_file()
	data = await new_file.download_as_bytearray()
	text, keyboard = entry_photo(user_id, data)
	try:
		if keyboard:
			await update.message.reply_text(text=text,
											reply_markup=InlineKeyboardMarkup(kbd_to_inline(keyboard))
											)
		else:
			await update.message.reply_text(text=text)

	except Exception as e:
		my_logger.error('Exception cb_user_photo ', e)


async def cb_cmd_gen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	cmd = update.message.text

	try:
		user_id = update['message']['from']['id']
		user = Db.get_user(user_id)
		if user["apm"]["place_id"] != SUPERVISOR_ARM:
			await update.message.reply_text("❌ Команда запрещена")
			return None
	except Exception as e:
		my_logger.error('Exception cb_cmd_gen ', e)
		# todo Local variable 'user_id' might be referenced before assignment
		await update.message.reply_text(f'Здравствуйте {user['name']}!\n⚠ Введите пароль')
		return None

	try:
		cmds = cmd.split(' ')

		start_number = QRCodeStorage.get_qr_start_value()
		end_number = start_number
		if cmds[0] == f'/{qr_cmd_gen24}':
			end_number = start_number + 24
		elif cmds[0] == f'/{qr_cmd_gen48}':
			end_number = start_number + 48
		elif cmds[0] == f'/{qr_cmd_gen72}':
			end_number = start_number + 72
		elif cmds[0] != f'/{qr_cmd_old}' or len(cmds) != 2:
			raise Exception("Unknown command")

		msg = await update.message.reply_text("⏳ Генерация QR-кодов..")

		if end_number == start_number:  # Old records
			codes = sorted(set(re.findall(r'\d+', cmds[1])))
			pdf_name, pdf_data = gen_pdf(codes)
		else:  # Gen new records
			pdf_name, pdf_data = gen_pdf([str(code) for code in range(start_number, end_number)])
			QRCodeStorage.set_qr_start_value(end_number)

		await msg.delete()
		await update.message.reply_document(document=pdf_data, filename=pdf_name, caption=TEXT_QR_CODES_READY)
	except Exception as e:
		my_logger.error(f'Exception cb_cmd_gen {e}')
		text = f"❌ Неправильный ввод: {cmd}\n"
		text += f'/{qr_cmd_gen24} - генерация 24 новых QR-кодов\n'
		text += f'/{qr_cmd_gen48} - генерация 48 новых QR-кодов\n'
		text += f'/{qr_cmd_gen72} - генерация 72 новых QR-кодов\n'
		text += f'/{qr_cmd_old} N1,N2 - получение существующих N1,N2,.. QR-кодов\n'
		await update.message.reply_text(text)


async def main() -> None:
	application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

	application.add_handler(CommandHandler(qr_cmd_gen24, cb_cmd_gen))
	application.add_handler(CommandHandler(qr_cmd_gen48, cb_cmd_gen))
	application.add_handler(CommandHandler(qr_cmd_gen72, cb_cmd_gen))
	application.add_handler(CommandHandler(qr_cmd_old, cb_cmd_gen))
	application.add_handler(CommandHandler("start", cb_user_message))
	application.add_handler(MessageHandler(filters.TEXT, cb_user_message))
	application.add_handler(MessageHandler(filters.PHOTO, cb_user_photo))

	application.add_handler(CallbackQueryHandler(cb_user_button))

	await application.initialize()
	await application.start()
	await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

	my_logger.info("Bot 'Registry Birds v1.1.0' enabled")

	while True:
		await asyncio.sleep(SLEEP)

	# todo This code is unreachable
	await application.updater.stop()
	my_logger.info("Bot disabled")

	await application.shutdown()


if __name__ == "__main__":
	asyncio.run(main())
