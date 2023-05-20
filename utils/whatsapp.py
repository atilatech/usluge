from twilio.rest import Client

from utils.credentials import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WHATSAPP_NUMBER

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


def send_whatsapp_message(text, destination_number: str):
    print('send_whatsapp_message', text, destination_number)
    if not destination_number.startswith('whatsapp:'):
        destination_number = f'whatsapp:{destination_number}'

    destination_number = destination_number.replace(' ', '')
    message = client.messages.create(
        from_=f'whatsapp:{WHATSAPP_NUMBER}',
        body=text,
        to=f'{destination_number}'  # Add your WhatsApp No. here
    )
    print(message.sid)
