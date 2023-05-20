import string
import time
from collections import defaultdict

import telegram
from telegram import Bot, Update
from telegram.ext import ContextTypes

from utils.credentials import BOT_TOKEN
from utils.database import database
from utils.telegram import telegram_bot
from utils.utils import get_random_string, RIDE_REQUESTS_KEY, LIST_COMMAND_BUTTON, HELP_COMMAND_BUTTON, \
    DRIVER_COMMAND_BUTTON
from utils.whatsapp import send_whatsapp_message

drivers_debug = [
    # {
    #     'username': 'IvanKapisoda',
    #     'first_name': 'Ivan',
    #     'id': '1642664602',
    # },
    {
        'username': 'tomiwa1a1',
        'first_name': 'Tomiwa',
        'id': '5238299107',
        'phone': '+1905 875 8867',
    },
]

drivers = drivers_debug


def get_matching_ride_request(target_driver_id, bot_data):
    ride_requests = bot_data[RIDE_REQUESTS_KEY]
    for rider_id, ride_request in ride_requests.items():
        if ride_request['driver'] is not None:
            driver_id = ride_request['driver']['id']
            if driver_id == target_driver_id:
                return ride_request

    return None


def create_ride_request(rider: dict, request_text: str, chat_id: str):
    chat_id = str(chat_id)
    request_id = get_random_string()
    accept_code = get_random_string(6, string.digits)
    ride_request = {
        'id': request_id,
        'accept_code': accept_code,
        'rider': {
            'first_name': rider.get('first_name', None),
            'telegram_username': rider.get('telegram_username', None),
            'telegram_id': rider.get('telegram_id', None),
            'phone': rider.get('phone', None),
        },
        'driver': None,
        'request': request_text,
        'price': None,
        'offers': {},
        'date_created': int(time.time())
    }

    print('ride_request', ride_request)
    database['ride_requests'].insert_one(ride_request)

    database['active_request_ids'].update_one(
        {'chat_id': chat_id},
        {'$set': {'chat_id': chat_id, 'request_id': request_id}},
        upsert=True
    )

    return ride_request


def create_offer(context: ContextTypes.DEFAULT_TYPE,
                 service_request_id: str,
                 driver: telegram.User, price: str | int | float):
    offer_id = get_random_string()

    offer = {
        'id': offer_id,
        'driver': {
            'first_name': driver.first_name,
            'username': driver.username,
            'id': driver.id,
        },
        'price': price,
    }

    context.bot_data[RIDE_REQUESTS_KEY][service_request_id]['offers'][offer_id] = offer
    return offer


async def notify_drivers(ride_request, rider_request_text):
    driver_request_message = f"New Driver Request from {ride_request['rider']['first_name']}: {rider_request_text}"
    for driver in drivers:
        if not driver.get('id', None) and not not driver.get('phone', None):
            print(f'No ID or phone for driver: {driver}')
            continue
        print('messaging driver: ', driver)
        print('update.message', rider_request_text)

        if 'phone' in driver and 'Tomiwa' in driver['first_name']:
            accept_code = ride_request['accept_code']
            cta_text = f"Reply {accept_code} to accept or 'd' to decline"
            send_whatsapp_message(f"{driver_request_message}\n\n{cta_text}", driver['phone'])

        if 'telegram_id' in driver:
            ride_id = ride_request['id']
            accept_callback_data = f"accept__{ride_id}"
            decline_callback_data = f"decline__{ride_id}"
            accept_button = telegram.InlineKeyboardButton(
                text='accept ✅',  # text that's shown to the user
                callback_data=accept_callback_data  # text send to the bot when user taps the button
            )
            decline_button = telegram.InlineKeyboardButton(
                text='decline 🚫',  # text that's shown to the user
                callback_data=decline_callback_data  # text send to the bot when user taps the button
            )

            async with telegram_bot:
                await telegram_bot.send_message(
                    chat_id=driver['telegram_id'],
                    text=driver_request_message,
                    reply_markup=telegram.InlineKeyboardMarkup([[accept_button, decline_button]])
                )


async def send_driver_requests(chat_id, rider, rider_request_text):
    ride_request = create_ride_request(rider, rider_request_text, str(chat_id))
    await notify_drivers(ride_request, rider_request_text)


async def get_driver_price(chat_id, bot: Bot):
    # Send the message with the number pad keyboard
    await bot.send_message(
        chat_id=chat_id,
        text="How much do you charge for this trip in Euros?",
    )


async def send_offer_to_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) not in context.bot_data['active_request_ids']:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="No Driver requests found for this chat. Type /list"
                                            "to see your requests")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"No Driver requests found for this chat. Type 'driver' to book a driver,"
                 f" /list to see your driver requests or /help",
            reply_markup=telegram.InlineKeyboardMarkup([[DRIVER_COMMAND_BUTTON,
                                                         LIST_COMMAND_BUTTON,
                                                         HELP_COMMAND_BUTTON]])
        )
        return None

    active_request_id = context.bot_data['active_request_ids'][str(update.effective_chat.id)]
    service_request = context.bot_data[RIDE_REQUESTS_KEY][active_request_id]
    driver = update.message.from_user
    price = update.message.text
    offer = create_offer(context, service_request['id'], driver, price)

    accept_callback_data = f"accept_offer__{offer['id']}"
    decline_callback_data = f"decline_offer__{offer['id']}"

    print('accept_callback_data', accept_callback_data)
    accept_button = telegram.InlineKeyboardButton(
        text='accept ✅',  # text that's shown to the user
        callback_data=accept_callback_data  # text send to the bot when user taps the button
    )
    decline_button = telegram.InlineKeyboardButton(
        text='decline 🚫',  # text that's shown to the user
        callback_data=decline_callback_data  # text send to the bot when user taps the button,
    )
    await context.bot.send_message(
        chat_id=service_request['rider']['id'],
        text=f"Taxi Offer from {driver['first_name']}: {price} euros for '{service_request['request']}'",
        reply_markup=telegram.InlineKeyboardMarkup([[accept_button, decline_button]])
    )

    return service_request
