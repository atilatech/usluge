import telegram
from telegram import Bot, Update
from telegram.ext import ContextTypes

from utils.utils import get_random_string, RIDE_REQUESTS_KEY

drivers = [
    # {
    #     'username': 'IvanKapisoda',
    #     'first_name': 'Ivan',
    #     'id': '1642664602',
    # },
    {
        'username': 'Tomiwa',
        'first_name': 'tomiwa1a1',
        'id': '5238299107',
    },
]


def get_matching_ride_request(target_driver_id, bot_data):
    ride_requests = bot_data[RIDE_REQUESTS_KEY]
    for rider_id, ride_request in ride_requests.items():
        if ride_request['driver'] is not None:
            driver_id = ride_request['driver']['id']
            if driver_id == target_driver_id:
                return ride_request

    return None


def create_ride_request(context: ContextTypes.DEFAULT_TYPE, rider: telegram.User, text: str):
    ride_request = {
        'id': get_random_string(),
        'rider': {
            'first_name': rider.first_name,
            'username': rider.username,
            'id': str(rider.id),
        },
        'driver': None,
        'request': text,
        'response': None,
    }
    if RIDE_REQUESTS_KEY not in context.bot_data:
        context.bot_data[RIDE_REQUESTS_KEY] = {}

    context.bot_data[RIDE_REQUESTS_KEY][str(rider.id)] = ride_request

    return context.bot_data[RIDE_REQUESTS_KEY]


def update_ride_request_accept_ride(rider_id, driver: telegram.User, context: ContextTypes.DEFAULT_TYPE):
    driver = {
        'first_name': driver.first_name,
        'username': driver.username,
        'id': str(driver.id),
    }

    context.bot_data[RIDE_REQUESTS_KEY][rider_id]['driver'] = driver

    return context.bot_data[RIDE_REQUESTS_KEY]


async def find_taxi(update: Update, bot: Bot, context: ContextTypes.DEFAULT_TYPE, driver_request):
    create_ride_request(context, update.message.from_user, driver_request)

    await bot.send_message(
        chat_id=update.message.from_user.id,
        text=f"We are looking for drivers for the following request: {driver_request}\n\n"
    )

    for driver in drivers:
        print('messaging driver: ', driver)
        print('update.message', driver_request)
        print('context.bot_data', context.bot_data)
        accept_callback_data = f"accept__{update.message.from_user.id}"
        decline_callback_data = f"decline__{update.message.from_user.id}"
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
            text=driver_request,
            reply_markup=telegram.InlineKeyboardMarkup([[accept_button, decline_button]])
        )


async def get_driver_price(chat_id, bot: Bot):
    # Send the message with the number pad keyboard
    await bot.send_message(
        chat_id=chat_id,
        text="How much do you charge for this trip in Euros?",
    )


async def confirm_price_with_rider(request, amount, rider_id, driver_name, bot):
    accept_callback_data = f"accept_offer"
    decline_callback_data = f"decline_offer"

    accept_button = telegram.InlineKeyboardButton(
        text='accept ✅',  # text that's shown to the user
        callback_data=accept_callback_data  # text send to the bot when user taps the button
    )
    decline_button = telegram.InlineKeyboardButton(
        text='decline 🚫',  # text that's shown to the user
        callback_data=decline_callback_data  # text send to the bot when user taps the button
    )
    await bot.send_message(
        chat_id=rider_id,
        text=f"Taxi Offer from {driver_name}: {amount} euros for '{request}'",
        reply_markup=telegram.InlineKeyboardMarkup([[accept_button, decline_button]])
    )
