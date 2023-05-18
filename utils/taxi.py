import telegram
from telegram import Bot

drivers = [
    {
        'username': 'IvanKapisoda',
        'first_name': 'Ivan',
        'user_id': '1642664602',
    },
]


async def find_taxi(request, bot: Bot):
    for driver in drivers:
        print('update.message', request)
        custom_keyboard = [['accept ✅', 'decline 🚫']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
        await bot.send_message(
            chat_id=driver['user_id'],
            text=f"Taxi Request: {request}",
            reply_markup=reply_markup
        )
        await bot.send_message(chat_id=driver['user_id'], text=f'Rider Requesting a taxi: {request}')


async def get_driver_price(chat_id, bot: Bot):

    # Send the message with the number pad keyboard
    await bot.send_message(
        chat_id=chat_id,
        text="How much do you charge?",
    )
