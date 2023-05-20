from flask import Flask, request

from utils.ai import check_enough_info_to_make_request, ai_true_key
from utils.credentials import WHATSAPP_NUMBER
from utils.taxi import send_driver_requests
from utils.whatsapp import send_whatsapp_message

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return 'Welcome to usluge'


@app.route('/whatsapp', methods=['POST'])
async def whatsapp():
    print('/whatsapp')
    print('request.form', request.form)
    incoming_msg = request.form.get('Body').lower()
    incoming_number = request.form.get('WaId')

    if WHATSAPP_NUMBER in incoming_number:
        return 'this number is from the bot'

    enough_info_to_make_request = check_enough_info_to_make_request(incoming_msg)

    if ai_true_key in enough_info_to_make_request:
        reply = f"Sending driver requests: {incoming_msg}"
        chat_id = incoming_number
        rider = {
            'phone': incoming_number,
            'first_name': request.form.get('ProfileName'),
        }
        await send_driver_requests(chat_id, rider, incoming_msg)
    else:
        reply = enough_info_to_make_request

    print('response, reply', incoming_msg, reply)
    send_whatsapp_message(reply, incoming_number)

    return reply


if __name__ == '__main__':
    # send_whatsapp_message('testing', '+19058758867')
    app.run(debug=True)
