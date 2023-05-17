from datetime import datetime

import gspread
import pytz
from telegram import Message

from bot_helpers.credentials import GOOGLE_SERVICE_ACCOUNT_CREDENTIALS

USLUGE_USERS_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16e70m-8SeM1F2suA7rOunico2ASH5xEa_KwdeFbeqMA" \
                               "/edit#gid=0"

# Authenticate using the loaded credentials
gc = gspread.service_account_from_dict(GOOGLE_SERVICE_ACCOUNT_CREDENTIALS)

# Open the Google Spreadsheet by its URL
spreadsheet = gc.open_by_url(USLUGE_USERS_SPREADSHEET_URL)


def save_message_response(response, message):
    message_response = create_dict_from_message(message)
    message_response['response'] = response

    print('message_response', message_response)
    append_message_to_sheet(message_response)
    return message_response


def create_dict_from_message(message: Message):
    text = message.text.encode('utf-8').decode()
    chat_id = message.chat.id
    msg_id = message.message_id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    unix_timestamp = message.date.timestamp()

    datetime_object = datetime.fromtimestamp(unix_timestamp)
    # Convert the datetime object to GMT+2
    # Specify the Montenegro timezone
    timezone = pytz.timezone('Europe/Podgorica')
    # Convert datetime_object to Montenegro timezone
    datetime_object_gmt2 = datetime_object.astimezone(timezone)

    # Format the datetime object as a human-readable string
    human_readable_date = datetime_object_gmt2.strftime('%A, %B %d, %Y %I:%M %p')

    message_data = {
        'text': text,
        'chat_id': chat_id,
        'message_id': msg_id,
        'user_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'date': unix_timestamp,
        'human_readable_date': human_readable_date
    }

    return message_data


def append_message_to_sheet(data_to_save):
    # Select the first sheet in the spreadsheet
    sheet = spreadsheet.get_worksheet(0)

    # Get the last row index in the sheet
    last_row_index = len(sheet.get_all_values()) + 1

    # Retrieve the header row
    header_row = sheet.row_values(1)

    # Prepare the values to be appended to the sheet
    values = [data_to_save.get(header, "") for header in header_row]

    # Append the values to the last row of the sheet
    sheet.insert_row(values, last_row_index)

    print('Data appended successfully to the Google Spreadsheet.')


if __name__ == "__main__":
    # Example usage
    data = {
        'telegram_user_id': 123456789,
        'telegram_username': 'john_doe',
        'date_human_readable': 'Wednesday, May 12, 2023 5:55 PM',
        'first_name': 'John',
        'last_name': 'Doe',
        'date': '2023-05-12',
        'text': 'Sample text message'
    }

    append_message_to_sheet(data)
