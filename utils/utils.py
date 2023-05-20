import random
import string
import time
from datetime import datetime

import pytz
import telegram

RIDE_REQUESTS_KEY = 'ride_requests'

bot_data_file_path = "bot_data"

request_requirements = "pickup and drop off location, pickup time and number of people"


def get_random_string(length=16):
    # choose from all lowercase letter
    options = string.ascii_lowercase + string.digits
    result_str = ''.join(random.choice(options) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str


DRIVER_COMMAND_BUTTON = telegram.InlineKeyboardButton(
    text='/driver',  # text that's shown to the user
    callback_data='/driver'  # text send to the bot when user taps the button
)

HELP_COMMAND_BUTTON = telegram.InlineKeyboardButton(
    text='/help',  # text that's shown to the user
    callback_data='/help'  # text send to the bot when user taps the button
)

LIST_COMMAND_BUTTON = telegram.InlineKeyboardButton(
    text='/list',
    callback_data='/list'
)


def get_do_nothing_button(text):
    return telegram.InlineKeyboardButton(
        text=text,
        callback_data='/nothing'
    )


def human_readable_date(unix_timestamp=None):
    if unix_timestamp is None:
        unix_timestamp = time.time()

    datetime_object = datetime.fromtimestamp(unix_timestamp)
    # Convert the datetime object to GMT+2
    # Specify the Montenegro timezone
    timezone = pytz.timezone('Europe/Podgorica')
    # Convert datetime_object to Montenegro timezone
    datetime_object_gmt2 = datetime_object.astimezone(timezone)
    # Format the datetime object as a human-readable string
    return datetime_object_gmt2.strftime('%A, %B %d, %Y %I:%M %p')
