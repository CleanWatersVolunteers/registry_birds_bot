import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
import botmenu
from datetime import datetime
from storage import storage
from logs import log

f = open('token', 'r')
TELEGRAM_BOT_TOKEN = f.read()
f.close()

log.init("logs.txt")
storage.init("user.base","birds.base")


async def main() -> None:
	application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

	application.add_handler(CommandHandler("start", botmenu.cb_message_entry))
	application.add_handler(MessageHandler(filters.TEXT, botmenu.cb_message_entry))

	application.add_handler(CallbackQueryHandler(botmenu.cb_reaction_button))

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

