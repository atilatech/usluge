import time

import telegram
from telegram import Bot, Update
from telegram.ext import ContextTypes

from utils.save_data import get_drivers
from utils.utils import get_random_string, RIDE_REQUESTS_KEY, LIST_COMMAND_BUTTON, HELP_COMMAND_BUTTON, \
    DRIVER_COMMAND_BUTTON

drivers_debug = [
    {
        'username': 'IvanKapisoda',
        'first_name': 'Ivan',
        'id': '1642664602',
    },
    # {
    #     'username': 'Tomiwa',
    #     'first_name': 'tomiwa1a1',
    #     'id': '5238299107',
    # },
]

drivers = get_drivers()


def get_matching_ride_request(target_driver_id, bot_data):
    ride_requests = bot_data[RIDE_REQUESTS_KEY]
    for rider_id, ride_request in ride_requests.items():
        if ride_request['driver'] is not None:
            driver_id = ride_request['driver']['id']
            if driver_id == target_driver_id:
                return ride_request

    return None


def create_ride_request(context: ContextTypes.DEFAULT_TYPE, rider: telegram.User, text: str, update: Update):
    request_id = get_random_string()
    ride_request = {
        'id': request_id,
        'rider': {
            'first_name': rider.first_name,
            'username': rider.username,
            'id': rider.id,
        },
        'driver': None,
        'request': text,
        'price': None,
        'offers': {},
        'date_created': int(time.time())
    }
    if RIDE_REQUESTS_KEY not in context.bot_data:
        context.bot_data[RIDE_REQUESTS_KEY] = {}

    context.bot_data[RIDE_REQUESTS_KEY][request_id] = ride_request
    if 'active_request_ids' not in context.bot_data:
        context.bot_data['active_request_ids'] = {}

    context.bot_data['active_request_ids'][str(update.effective_chat.id)] = request_id

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


async def find_taxi(update: Update, bot: Bot, context: ContextTypes.DEFAULT_TYPE, driver_request):
    ride_request = create_ride_request(context, update.message.from_user, driver_request, update)
    ride_id = ride_request['id']

    await bot.send_message(
        chat_id=update.message.from_user.id,
        text=f"We are looking for drivers for the following request: {driver_request}\n\n"
    )

    for driver in drivers:
        if not driver.get('id', None):
            print(f'No ID for driver: {driver}')
            continue
        print('messaging driver: ', driver)
        print('update.message', driver_request)
        print('context.bot_data', context.bot_data)
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
        await bot.send_message(
            chat_id=driver['id'],
            text=f"New Driver Request: {driver_request}",
            reply_markup=telegram.InlineKeyboardMarkup([[accept_button, decline_button]])
        )


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
