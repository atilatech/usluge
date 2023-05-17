import re
import telegram
from flask import Flask, request
from telebot.credentials import bot_token, BOT_DEPLOYMENT_URL, SENTRY_DSN
from telebot.find_services import find_service_provider
import asyncio

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from telebot.save_data import save_message, save_message_response, is_repeated_update, update_latest_update_id

# Increase timeout to avoid:
# Telegram.error.TimedOut: Pool timeout: All connections in the connection pool are occupied.
# Request was *not* sent to Telegram. Consider adjusting the connection pool size or the pool timeout.
telegram_request = telegram.request.HTTPXRequest(connection_pool_size=10, read_timeout=25.0, write_timeout=25.0,
                                                 connect_timeout=25.0, pool_timeout=25.0)

TOKEN = bot_token
bot = telegram.Bot(token=TOKEN, request=telegram_request)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        FlaskIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

# start the flask app
app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
async def respond():
    # retrieve the message in JSON and then transform it to Telegram object

    json_data = request.get_json(force=True)
    update = telegram.Update.de_json(json_data, bot)
    print('json_data', json_data)
    # Get the current update_id
    current_update_id = update.update_id

    # Check if it's a repeated update
    if is_repeated_update(current_update_id):
        # Ignore repeated update
        return 'Repeated update', 200

    if not update or not update.message or not update.message.chat:
        return f"bad request! No update found, just {json_data}", 400

    update_latest_update_id(current_update_id)
    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for Unicode compatibility
    saved_message = save_message(update.message)
    text = saved_message['text']

    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
       Welcome to Usluge, a place for finding services in Montenegro.
       Examples you can send in the chat:
       1. find cleaners Tivat
       2. find hairdresser Budva
       If you need help, send /help or message @IvanKapisoda.
       ---
       Dobrodošli u Usluge, mjesto za pronalaženje usluga u Crnoj Gori.
         Primeri koje možete poslati u ćaskanju:
         1. naći čistače Tivat
         2. naći frizer Budva
         Ako vam je potrebna pomoć, pošaljite /help ili poruku @IvanKapisoda.
       """
        # send the welcoming message
        try:
            await bot.send_message(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
        except telegram.error.TimedOut as e:
            print('telegram.error.TimedOut', str(e))
            return f"bad request! {str(e)}", 400
    else:
        await bot.send_chat_action(chat_id=chat_id, action=telegram.constants.ChatAction.TYPING)
        response = find_service_provider(text)
        save_message_response(response, update.message)
        print("find_service_provider response", response)
        await bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which lives
    # in the link provided by URL
    webhook = '{URL}/{HOOK}'.format(URL=BOT_DEPLOYMENT_URL, HOOK=TOKEN)
    print(webhook)
    s = bot.setWebhook(webhook)
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return 'Welcome to Usluge'


@app.route('/debug-sentry')
def trigger_error():
    # Throw a divide by Zero error to verify that Sentry works
    return 1 / 0


async def run_flask_app():
    app.run(threaded=True)


if __name__ == '__main__':
    # Run the Flask app asynchronously
    asyncio.run(run_flask_app())
