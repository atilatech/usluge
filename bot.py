import logging

import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, PicklePersistence, \
    CallbackQueryHandler

from utils.credentials import BOT_TOKEN
from utils.prompt import get_conversation_chain
from utils.save_data import save_message_response, save_bot_data
from utils.taxi import find_taxi, get_driver_price, send_offer_to_client
from utils.utils import RIDE_REQUESTS_KEY, get_do_nothing_button, bot_data_file_path

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_welcome = """
           Book a driver for Edcon and Luštica\n\n(Taxis run between Chedi, Lustica Bay and Podgorica).
           Start your sentence with 'taxi' and then your pickup and drop off location.
           Example:\n
           Taxi from Chedi hotel lustica bay to UDG podgorica
           """
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=bot_welcome,
                                   reply_to_message_id=update.message.message_id)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = ''
    if update.message.text.isdigit():
        await send_offer_to_client(update, context)
    else:
        response = get_conversation_chain(context).predict(human_input=update.message.text)
        if 'New Driver Request:' in response:
            driver_request = response.split('New Driver Request:')[1]
            await find_taxi(update, application.bot, context, driver_request)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    save_message_response(response, update.message, context)


async def accept_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cqd = update.callback_query.data
    # message_id = update.callback_query.message.message_id
    # update_id = update.update_id
    if cqd.startswith('accept__'):
        active_request_id = cqd.split('__')[1]
        context.chat_data['active_request_id'] = active_request_id
        active_request = context.bot_data[RIDE_REQUESTS_KEY][active_request_id]
        driver = update.callback_query.from_user
        text = f'Your ride has been accepted by {driver.first_name}.\nWaiting for them to send their price.'
        print('request_id, driver', active_request_id, driver)
        print('context.bot_data', context.bot_data)
        await context.bot.send_message(chat_id=active_request['rider']['id'], text=text)
        await get_driver_price(driver.id, context.bot)

    if cqd.startswith('accept_offer'):
        offer_id = cqd.split('__')[1]

        active_request_id = context.chat_data['active_request_id']
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

    print('chat_shared', chat_shared)
    print('update.message', update.message)
    print('chat_id', chat_id)
    print('context.bot.get_chat_members(chat_id)', context.bot.get_chat_members(chat_id))
    print('update.message.new_chat_members', update.message.new_chat_members)


if __name__ == '__main__':
    persistence = PicklePersistence(filepath=bot_data_file_path)
    application = ApplicationBuilder().token(BOT_TOKEN).persistence(persistence).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(CommandHandler('save', save_bot_data))

    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
    application.add_handler(chat_handler)

    accept_ride_handler = CallbackQueryHandler(accept_ride)
    application.add_handler(accept_ride_handler)

    new_message_handler = CallbackQueryHandler(accept_ride)
    chat_shared_handler = MessageHandler(filters.StatusUpdate.CHAT_SHARED |
                                         filters.StatusUpdate.CHAT_CREATED,
                                         chat_shared)
    application.add_handler(chat_shared_handler)

    application.run_polling()
