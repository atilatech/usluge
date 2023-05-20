import logging

import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, PicklePersistence, \
    CallbackQueryHandler

from utils.ai import check_enough_info_to_make_request, ai_true_key
from utils.credentials import BOT_TOKEN
from utils.database import database
from utils.save_data import save_message_response, save_bot_data
from utils.taxi import send_driver_requests, send_offer_to_rider, notify_driver_rider_accepts_offer, \
    driver_accepts_rider_request
from utils.utils import get_do_nothing_button, bot_data_file_path, request_requirements

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_welcome = f"""
           Book a driver in Montenegro.
           Please include: {request_requirements}.
           Example:\n
           pickup from Chedi hotel lustica bay to UDG podgorica, 5pm today, 3 people
           """
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=bot_welcome,
                                   reply_to_message_id=update.message.message_id)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = ''
    message_text = update.message.text

    user = {
        'first_name': update.message.from_user.first_name,
        'telegram_username': update.message.from_user.username,
        'telegram_id': update.message.from_user.id,
        'source': 'telegram'
    }
    if message_text.isdigit():
        ride_request_id = database['active_request_ids'].find_one({
            'chat_id': update.effective_chat.id})
        await send_offer_to_rider(message_text, user, ride_request_id['request_id'])
    else:
        # Replace AI logic with a simple if statement if we need to save on LLM costs or LLM logic is not working
        # if len(message_text.split(' ')) < 4:
        enough_info_to_make_request = check_enough_info_to_make_request(message_text)
        if ai_true_key in enough_info_to_make_request.lower():

            await context.bot.send_message(
                chat_id=update.message.from_user.id,
                text=f"We are looking for drivers for your request: {message_text}\n\n"
                     f"We'll let you know as soon as we receive an order."
            )
            await send_driver_requests(update.effective_chat.id, user, context)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=enough_info_to_make_request)

    save_message_response(response, update.message, context)


async def accept_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cqd = update.callback_query.data
    if cqd.startswith('accept__'):
        # driver accepts rider's request
        ride_request_id = cqd.split('__')[1]
        ride_request = database['ride_requests'].find_one({'id': ride_request_id})
        print(ride_request)

        database['active_request_ids'].update_one(
            {'chat_id': update.effective_chat.id},
            {'$set': {'chat_id': update.effective_chat.id, 'request_id': ride_request['id']}},
            upsert=True
        )
        driver = {
            'first_name': update.callback_query.from_user.first_name,
            'telegram_username': update.callback_query.from_user.username,
            'telegram_id': update.callback_query.from_user.id
        }
        await driver_accepts_rider_request(ride_request, driver)

    if cqd.startswith('accept_offer'):
        offer_id = cqd.split('__')[1]
        await notify_driver_rider_accepts_offer(update.effective_chat.id, offer_id)

    if cqd.startswith('decline_offer'):
        text = "Offer was declined"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    reply_markup = None
    if cqd.startswith('accept'):
        # driver accepts rider's request
        reply_markup = telegram.InlineKeyboardMarkup([[get_do_nothing_button('request was accepted')]])
    elif cqd.startswith('decline'):
        reply_markup = telegram.InlineKeyboardMarkup([[get_do_nothing_button('request was declined')]])

    await update.callback_query.edit_message_reply_markup(reply_markup)


async def chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    print('chat_shared')
    print('update.message', update.message)
    print('chat_id', chat_id)


if __name__ == '__main__':
    persistence = PicklePersistence(filepath=bot_data_file_path)
    application = ApplicationBuilder().token(BOT_TOKEN).persistence(persistence).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('save', save_bot_data))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    application.add_handler(CallbackQueryHandler(accept_ride))

    application.add_handler(MessageHandler(filters.StatusUpdate.CHAT_SHARED |
                                           filters.StatusUpdate.CHAT_CREATED,
                                           chat_shared))

    application.run_polling()
