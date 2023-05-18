import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from bot_helpers.credentials import BOT_TOKEN
from bot_helpers.generate_response import generate_response
from bot_helpers.save_data import save_message_response

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_welcome = """
           Welcome to Usluge, a place for finding services in Montenegro.
           Examples you can send in the chat:
           1. find cleaners Podgorica
           2. find hairdresser Budva
           If you need help, send /help or message @IvanKapisoda.
           ---
           Dobrodošli u Usluge, mjesto za pronalaženje usluga u Crnoj Gori.
             Primeri koje možete poslati u ćaskanju:
             1. naći čistače Podgorica
             2. naći frizer Budva
             Ako vam je potrebna pomoć, pošaljite /help ili poruku @IvanKapisoda.
           """
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=bot_welcome,
                                   reply_to_message_id=update.message.message_id)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    response = generate_response(update.message.text)['answer']
    save_message_response(response, update.message)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)

    application.add_handler(start_handler)
    application.add_handler(chat_handler)

    application.run_polling()
