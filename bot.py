import logging
from collections import defaultdict

import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, PicklePersistence, \
    CallbackQueryHandler

from utils.ai import check_enough_info_to_make_request, ai_true_key
from utils.credentials import BOT_TOKEN
from utils.save_data import save_message_response, save_bot_data
from utils.taxi import send_driver_requests, get_driver_price, send_offer_to_client
from utils.utils import RIDE_REQUESTS_KEY, get_do_nothing_button, bot_data_file_path, request_requirements

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
    if message_text.isdigit():
        await send_offer_to_client(update, context)
    else:
        # Replace AI logic with a simple if statement if we need to save on LLM costs or LLM logic is not working
        # if len(message_text.split(' ')) < 4:
        enough_info_to_make_request = check_enough_info_to_make_request(message_text)
        if ai_true_key in enough_info_to_make_request.lower():

            rider = {
                'first_name': update.message.from_user.first_name,
                'telegram_username': update.message.from_user.username,
                'telegram_id': update.message.from_user.id
            }

            await context.bot.send_message(
                chat_id=update.message.from_user.id,
                text=f"We are looking for drivers for your request: {message_text}\n\n"
                     f"We'll let you know as soon as we receive an order."
            )
            await send_driver_requests(update.effective_chat.id, rider, context)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=enough_info_to_make_request)

    save_message_response(response, update.message, context)


async def accept_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cqd = update.callback_query.data
    # message_id = update.callback_query.message.message_id
    # update_id = update.update_id
    if cqd.startswith('accept__'):
        active_request_id = cqd.split('__')[1]
        context.bot_data['active_request_ids'][str(update.effective_chat.id)] = active_request_id
        active_request = context.bot_data[RIDE_REQUESTS_KEY][active_request_id]
        driver = update.callback_query.from_user
        text = f'Your ride has been accepted by {driver.first_name}.\nWaiting for them to send their price.'
        print('request_id, driver', active_request_id, driver)
        await context.bot.send_message(chat_id=active_request['rider']['id'], text=text)
        await get_driver_price(driver.id, context.bot)

    if cqd.startswith('accept_offer'):
        offer_id = cqd.split('__')[1]

        active_request_id = context.bot_data['active_request_ids'][str(update.effective_chat.id)]
        service_request = context.bot_data[RIDE_REQUESTS_KEY][active_request_id]

        offer = service_request['offers'][offer_id]

        driver = offer['driver']
        price = offer['price']

        # set driver and price for the service request to the value from the driver
        context.bot_data[RIDE_REQUESTS_KEY][active_request_id]['driver'] = driver
        context.bot_data[RIDE_REQUESTS_KEY][active_request_id]['price'] = price

        service_request = context.bot_data[RIDE_REQUESTS_KEY][active_request_id]

        message_template = "Taxi Confirmed! {first_name} (@{username}) will message " \
                           "you shortly to arrange a pickup.\n\n" \
                           "Details: {request} \n" \
                           "Price: {response} Euros \n" \
                           'You can also send them a message: https://t.me/{username}.\n' \
            # 'Tip: Add @uslugebot to your chat with {first_name} to instantly add trip details and
        # price.'

        rider_message = message_template.format(first_name=service_request['driver']['first_name'],
                                                username=service_request['driver']['username'],
                                                request=service_request['request'],
                                                response=service_request['price'])

        driver_message = message_template.format(first_name=service_request['rider']['first_name'],
                                                 username=service_request['rider']['username'],
                                                 request=service_request['request'],
                                                 response=service_request['price'])

        print('rider_message, driver_message', rider_message, driver_message)
        await context.bot.send_message(chat_id=service_request['rider']['id'], text=rider_message)
        await context.bot.send_message(chat_id=service_request['driver']['id'], text=driver_message)

    if cqd.startswith('decline_offer'):
        text = "Offer was declined"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    reply_markup = None
    if cqd.startswith('accept'):
        reply_markup = telegram.InlineKeyboardMarkup([[get_do_nothing_button('offer was accepted')]])
    elif cqd.startswith('decline'):
        reply_markup = telegram.InlineKeyboardMarkup([[get_do_nothing_button('offer was declined')]])

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
