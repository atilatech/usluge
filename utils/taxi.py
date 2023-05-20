import string
import time

import telegram

from utils.database import database
from utils.save_data import DATABASE_SPREADSHEET_URL, get_drivers
from utils.telegram import telegram_bot
from utils.utils import get_random_string, RIDE_REQUESTS_KEY
from utils.whatsapp import send_whatsapp_message

ivan_telegram_id = '1642664602'
tomiwa_telegram_id = '5238299107'

drivers_debug = [
    # {
    #     'telegram_username': 'IvanKapisoda',
    #     'first_name': 'Ivan',
    #     'telegram_id': ivan_telegram_id,
    # },
    {
        'username': 'tomiwa1a1',
        'first_name': 'Tomiwa',
        'telegram_id': tomiwa_telegram_id,
        'phone': '+1905 875 8867',
    },
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


def create_ride_request(rider: dict, request_text: str, chat_id: str):
    chat_id = str(chat_id)
    request_id = get_random_string()
    accept_code = get_random_string(6, string.digits)
    ride_request = {
        'id': request_id,
        'accept_code': accept_code,
        'rider': {
            'first_name': rider.get('first_name'),
            'telegram_username': rider.get('telegram_username'),
            'telegram_id': rider.get('telegram_id'),
            'phone': rider.get('phone'),
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


def create_offer(price: str | int | float,
                 driver: dict,
                 request_id: str):
    # start with '111' to distinguish from the 6 digit accept code
    offer_id = '111' + str(get_random_string(3, string.digits))

    offer = {
        'id': offer_id,
        'driver': driver,
        'price': price,
    }
    database['ride_requests'].update_one({'id': request_id}, {'$set': {f'offers.{offer_id}': offer}})

    return offer


async def notify_drivers(ride_request, rider_request_text):
    driver_request_message = f"New Driver Request from {ride_request['rider']['first_name']}: {rider_request_text}"
    for driver in drivers:
        if driver.get('phone'):
            print('Messaging', driver.get('first_name'), driver.get('phone'))
            accept_code = ride_request['accept_code']
            cta_text = f"Reply {accept_code} to accept or 'd' to decline"
            send_whatsapp_message(f"{driver_request_message}\n\n{cta_text}", driver['phone'])

        if driver.get('telegram_id'):
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


async def get_driver_price(driver):
    print('get_driver_price')
    text = "How much do you charge for this trip in Euros?"
    await send_telegram_or_whatsapp_message(driver, text)


async def send_offer_to_rider(price, driver, request_id):
    print('send_offer_to_rider')
    ride_request = database['ride_requests'].find_one({'id': request_id})
    print('ride_request', ride_request)
    offer = create_offer(price, driver, request_id)

    offer_message = f"Taxi Offer from {driver['first_name']}: {price} euros for '{ride_request['request']}'"

    if ride_request['rider'].get('telegram_id'):
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
        async with telegram_bot:
            await telegram_bot.send_message(
                chat_id=ride_request['rider']['telegram_id'],
                text=offer_message,
                reply_markup=telegram.InlineKeyboardMarkup([[accept_button, decline_button]])
            )

    elif ride_request['rider'].get('phone'):
        offer_message = f"{offer_message}\n\n reply {offer['id']} to accept or 'd' to decline"
        send_whatsapp_message(offer_message, ride_request['rider']['phone'])

    return ride_request


async def driver_accepts_rider_request(ride_request, driver):
    print('driver_accepts_rider_request')
    await get_driver_price(driver)
    text = f"Your ride has been accepted by {driver['first_name']}.\nWaiting for them to send their price."
    await send_telegram_or_whatsapp_message(ride_request['rider'], text)


async def notify_driver_rider_accepts_offer(chat_id, offer_id):
    ride_request_id = database['active_request_ids'].find_one({
        'chat_id': chat_id})
    ride_request = database['ride_requests'].find_one({'id': ride_request_id['request_id']})

    print('ride_request', ride_request)
    offer = ride_request['offers'][offer_id]
    rider = ride_request['rider']
    driver = ride_request['offers'][offer_id]['driver']

    database['ride_requests'].update_one(
        {'id': ride_request_id},
        {'$set': {'driver': driver, 'price': offer['price']}}
    )

    message_template = "Driver Confirmed!\n\n" \
                       "Details: {request} \n" \
                       "Price: {price} Euros \n" \
                       "Driver: {driver_name} {driver_contact}{driver_url}\n" \
                       "Rider: {rider_name} {rider_contact}{rider_url}\n" \
                       'Driver will message you shortly for pickup.' \
                       'You can also message the driver.\n'

    rider_url = f" https://t.me/{rider.get('telegram_username')}" if rider.get('telegram_username') else ''
    driver_url = f" https://t.me/{driver.get('telegram_username')}" if driver.get('telegram_username') else ''

    message = message_template.format(request=ride_request['request'],
                                      price=offer['price'],
                                      driver_name=driver['first_name'],
                                      driver_contact=driver.get('telegram_username') or driver.get('phone'),
                                      rider_name=rider['first_name'],
                                      rider_contact=rider.get('telegram_username') or rider.get('phone'),
                                      rider_url=rider_url,
                                      driver_url=driver_url)

    await send_telegram_or_whatsapp_message(driver, message)
    await send_telegram_or_whatsapp_message(rider, message)

    if rider.get('source') != driver.get('source'):
        debug_text = f'Rider and driver are on different platforms.\n' \
                     f'Chat ID: {chat_id}\n' \
                     f'See: {DATABASE_SPREADSHEET_URL}'
        async with telegram_bot:
            await telegram_bot.send_message(ivan_telegram_id,
                                            text=debug_text)
            await telegram_bot.send_message(tomiwa_telegram_id,
                                            text=debug_text)


async def send_telegram_or_whatsapp_message(user, text):
    if user.get('telegram_id'):
        async with telegram_bot:
            await telegram_bot.send_message(user['telegram_id'],
                                            text=text)
    elif user.get('phone'):
        send_whatsapp_message(text, user['phone'])
