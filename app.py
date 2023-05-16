import re
import telegram
from flask import Flask, request
from telebot.credentials import bot_token, bot_user_name, BOT_DEPLOYMENT_URL
from telebot.find_services import find_service_provider
import asyncio

TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

# start the flask app
app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
async def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for Unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)
    # for debugging purposes only
    print("got text message :", text)
    print("chat id :", chat_id)
    print("message id :", msg_id)
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        bot_welcome = """
       Welcome to Usluge, a bot for booking service providers in Montenegro.
       Start your sentence with 'book' to find a service provider.
       If you need help, send /help or message @IvanKapisoda.
       """
        # send the welcoming message
        await bot.send_message(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

    elif text.startswith("book"):
        response = find_service_provider(text)
        print("find_service_provider response", response)
        await bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
    else:
        try:
            # clear the message we got from any non-alphabets
            text = re.sub(r"\W", "_", text)
            # create the API link for the avatar based on http://avatars.adorable.io/
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
            # reply with a photo to the name the user sent,
            # note that you can send photos by URL and Telegram will fetch it for you
            await bot.send_photo(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
        except Exception as e:
            print("Exception", e)
            # if things went wrong
            await bot.send_message(chat_id=chat_id,
                                   text="There was a problem in the name you used, please enter a different name",
                                   reply_to_message_id=msg_id)

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
    return '.'


async def run_flask_app():
    app.run(threaded=True)
if __name__ == '__main__':
    # Run the Flask app asynchronously
    asyncio.run(run_flask_app())
