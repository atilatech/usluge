import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, PicklePersistence, \
    CallbackQueryHandler

from utils.credentials import BOT_TOKEN, bot_user_name
from utils.prompt import get_conversation_chain
from utils.save_data import save_message_response
from utils.taxi import find_taxi, get_driver_price, confirm_price_with_rider, get_matching_ride_request, \
    update_ride_request_accept_ride
from utils.utils import RIDE_REQUESTS_KEY

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
        ride_request = get_matching_ride_request(str(update.effective_chat.id), context.bot_data)

        rider_id = ride_request['rider']['id']
        context.bot_data[RIDE_REQUESTS_KEY][str(rider_id)]['response'] = update.message.text
        await confirm_price_with_rider(ride_request['request'],
                                       update.message.text,
                                       rider_id,
                                       ride_request['driver']['first_name'],
                                       context.bot)
    else:
        response = get_conversation_chain().predict(human_input=update.message.text)
        if 'New Driver Request:' in response:
            driver_request = response.split('New Driver Request:')[1]
            await find_taxi(update, application.bot, context, driver_request)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    save_message_response(response, update.message)


async def accept_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cqd = update.callback_query.data
    # message_id = update.callback_query.message.message_id
    # update_id = update.update_id
    if cqd.startswith('accept__'):
        requester_user_id = cqd.split('__')[1]
        driver = update.callback_query.from_user
        text = f'Your ride has been accepted by {driver.first_name}.\nWaiting for them to send their price.'
        print('requester_user_id, driver', requester_user_id, driver)
        update_ride_request_accept_ride(requester_user_id, driver, context)
        print('context.bot_data', context.bot_data)
        await context.bot.send_message(chat_id=requester_user_id, text=text)
        await get_driver_price(driver.id, context.bot)

    if cqd.startswith('accept_offer'):
        rider = update.callback_query.from_user
        ride_request = context.bot_data[RIDE_REQUESTS_KEY][str(rider.id)]

        message_template = "Taxi Confirmed! {first_name} (@{username}) will message " \
                           "you shortly to arrange a pickup.\n\n" \
                           "Details: {request} \n" \
                           "Price: {response} Euros \n" \
                           'You can also send them a message: https://t.me/{username}.\n' \
            # 'Tip: Add @uslugebot to your chat with {first_name} to instantly add trip details and
        # price.'

        rider_message = message_template.format(first_name=ride_request['driver']['first_name'],
                                                username=ride_request['driver']['username'],
                                                request=ride_request['request'],
                                                response=ride_request['response'])

        driver_message = message_template.format(first_name=ride_request['rider']['first_name'],
                                                 username=ride_request['rider']['username'],
                                                 request=ride_request['request'],
                                                 response=ride_request['response'])

        print('rider_message, driver_message', rider_message, driver_message)
        await context.bot.send_message(chat_id=ride_request['rider']['id'], text=rider_message)
        await context.bot.send_message(chat_id=ride_request['driver']['id'], text=driver_message)

    if cqd.startswith('decline_offer'):
        rider = update.callback_query.from_user
        ride_request = context.bot_data[RIDE_REQUESTS_KEY][str(rider.id)]

        text = "Offer was declined"

        await context.bot.send_message(chat_id=ride_request['rider']['id'], text=text)
        await context.bot.send_message(chat_id=ride_request['driver']['id'], text=text)
        context.bot_data[RIDE_REQUESTS_KEY][str(rider.id)]['driver'] = None


async def chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    print('chat_shared', chat_shared)
    print('update.message', update.message)
    print('chat_id', chat_id)
    print('context.bot.get_chat_members(chat_id)', context.bot.get_chat_members(chat_id))
    print('update.message.new_chat_members', update.message.new_chat_members)


if __name__ == '__main__':
    persistence = PicklePersistence(filepath="bot_data")
    application = ApplicationBuilder().token(BOT_TOKEN).persistence(persistence).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

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
