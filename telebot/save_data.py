from datetime import datetime

import gspread
from telegram import Message

from telebot.credentials import GOOGLE_SERVICE_ACCOUNT_CREDENTIALS

USLUGE_USERS_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16e70m-8SeM1F2suA7rOunico2ASH5xEa_KwdeFbeqMA/edit#gid=0"


def save_message(message: Message):
    dict_message = create_dict_from_message(message)
    append_dict_to_sheet(dict_message)
    return dict_message


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
    human_readable_date = datetime_object.strftime('%A, %B %d, %Y %I:%M %p')

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

    print('message_data', message_data)

    return message_data


def append_dict_to_sheet(data_to_save, spreadsheet_url=USLUGE_USERS_SPREADSHEET_URL):
    # Load the credentials data_to_save

    # Authenticate using the loaded credentials
    gc = gspread.service_account_from_dict(GOOGLE_SERVICE_ACCOUNT_CREDENTIALS)

    # Open the Google Spreadsheet by its URL
    spreadsheet = gc.open_by_url(spreadsheet_url)

    # Select the first sheet in the spreadsheet
    sheet = spreadsheet.get_worksheet(0)

    # Get the last row index in the sheet
    last_row_index = len(sheet.get_all_values()) + 1

    # Prepare the values to be appended to the sheet
    values = list(data_to_save.values())

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

    append_dict_to_sheet(data)
