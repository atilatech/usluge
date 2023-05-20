import asyncio

from flask import Flask, request

from utils.ai import check_enough_info_to_make_request, ai_true_key
from utils.credentials import WHATSAPP_NUMBER
from utils.database import database
from utils.taxi import send_driver_requests, send_offer_to_rider, driver_accepts_rider_request, \
    notify_driver_rider_accepts_offer
from utils.whatsapp import send_whatsapp_message
import datetime

app = Flask(__name__)

one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
unix_timestamp_one_hour_ago = int(one_hour_ago.timestamp())


@app.route('/', methods=['GET', 'POST'])
def index():
    return 'Welcome to usluge'


@app.route('/whatsapp', methods=['POST'])
async def whatsapp():
    print('/whatsapp')
    print('request.form', request.form)
    incoming_msg = request.form.get('Body').lower()
    incoming_number = request.form.get('WaId')
    first_name = request.form.get('ProfileName')

    if WHATSAPP_NUMBER in incoming_number:
        return 'this number is from the bot'

    if incoming_msg == 'd':
        send_whatsapp_message('Offer declined', incoming_number)
    if incoming_msg.isdigit():
        if len(incoming_msg) == 6:
            if incoming_msg.startswith('111'):
                # rider accepts driver's offer
                # tell driver the offer has been accepted
                await notify_driver_rider_accepts_offer(incoming_number, incoming_msg)
            else:
                # driver accepts rider's request
                ride_request = database['ride_requests'].find_one({
                    'accept_code': incoming_msg,
                    'driver': None,
                    'date_created': {'$gte': unix_timestamp_one_hour_ago}})
                print(ride_request)
                if ride_request is None:
                    send_whatsapp_message('Invalid acceptance code', incoming_number)
                else:
                    database['active_request_ids'].update_one(
                        {'chat_id': incoming_number},
                        {'$set': {'chat_id': incoming_number, 'request_id': ride_request['id']}},
                        upsert=True
                    )
                    driver = {
                        'phone': incoming_number,
                        'first_name': first_name
                    }
                    await driver_accepts_rider_request(ride_request, driver)
        else:
            active_request_id = database['active_request_ids'].find_one({
                'chat_id': incoming_number})

            driver = {
                'phone': incoming_number,
                'first_name': first_name,
                'source': 'whatsapp'
            }
            await send_offer_to_rider(incoming_msg, driver, active_request_id['request_id'])
            send_whatsapp_message('Your offer has been sent', incoming_number)

    else:
        enough_info_to_make_request = check_enough_info_to_make_request(incoming_msg)

        if ai_true_key in enough_info_to_make_request:
            reply = f"We are looking for drivers for your request: {incoming_msg}\n\n"
            f"We'll let you know as soon as we receive a driver."
            chat_id = incoming_number
            rider = {
                'phone': incoming_number,
                'first_name': first_name,
                'source': 'whatsapp'
            }
            await send_driver_requests(chat_id, rider, incoming_msg)
        else:
            reply = enough_info_to_make_request

        send_whatsapp_message(reply, incoming_number)

    return 'ok'


async def run_flask_app():
    app.run(threaded=True)

if __name__ == '__main__':
    # Run the Flask app asynchronously
    asyncio.run(run_flask_app())
