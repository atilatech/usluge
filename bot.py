import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from utils.credentials import BOT_TOKEN
from utils.prompt import get_conversation_chain
from utils.save_data import save_message_response
from utils.taxi import find_taxi, get_driver_price

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_welcome = """
           Welcome to Usluge, a place for finding services in Montenegro.
           Examples you can send in the chat:
           1. taxi from Chedi, Lustica Bay to UDG, Podgorica
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
    response = ''
    if update.message.text.startswith('taxi'):
        await find_taxi(update.message.text, application.bot)
    elif update.message.text.startswith('accept'):
        await get_driver_price(update.effective_chat.id, context.bot)
    else:
        response = get_conversation_chain().predict(human_input=update.message.text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    save_message_response(response, update.message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)

    application.add_handler(start_handler)
    application.add_handler(chat_handler)

    application.run_polling()
