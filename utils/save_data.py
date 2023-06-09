import json

import gspread
from telegram import Message, Update
from telegram.ext import ContextTypes

from utils.credentials import GOOGLE_SERVICE_ACCOUNT_CREDENTIALS
from utils.utils import human_readable_date, bot_data_file_path

DATABASE_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16e70m-8SeM1F2suA7rOunico2ASH5xEa_KwdeFbeqMA" \
                           "/edit#gid=0"

DRIVERS_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1NXF6HKJg0cKu1DuNv6okH9IG4YAYPh41RuYIEt7XlLk/edit" \
                          "#gid=450026456"

# Authenticate using the loaded credentials
gc = gspread.service_account_from_dict(GOOGLE_SERVICE_ACCOUNT_CREDENTIALS)

# Open the Google Spreadsheet by its URL
spreadsheet = gc.open_by_url(DATABASE_SPREADSHEET_URL)

drivers_spreadsheet = gc.open_by_url(DRIVERS_SPREADSHEET_URL)


def get_drivers():
    sheet = drivers_spreadsheet.get_worksheet_by_id(450026456)

    all_drivers = sheet.get_all_values()
    keys = all_drivers[0]
    all_drivers_transform = []
    for lst in all_drivers[1:]:
        # Create a dictionary for each list
        row_dict = {}
        for i, value in enumerate(lst):
            # Use the corresponding key for each value
            key = keys[i]
            row_dict[key] = value
        # Add the dictionary to the array
        all_drivers_transform.append(row_dict)
    return all_drivers_transform


def save_message_response(response, message: Message, context: ContextTypes.DEFAULT_TYPE):
    message_response = create_dict_from_message(message)
    message_response['response'] = response

    print('message_response', message_response)
    append_message_to_sheet(message_response)
    # append_message_to_chat_history(message_response, context)
    return message_response


def append_message_to_chat_history(message, context: ContextTypes.DEFAULT_TYPE):
    chat_id = message['chat_id']

    if 'chat_history' not in context.bot_data:
        context.bot_data['chat_history'] = {}

    if chat_id not in context.bot_data['chat_history']:
        context.bot_data['chat_history'][chat_id] = []

    history = context.bot_data['chat_history'][chat_id]

    # only keep the 10 most recent messages to avoid filling this up too much
    history.append({
        'user': message['text'],
    })
    history.append({
        'bot': message['response'],
    })
    history = history[:10]
    context.bot_data['chat_history'][chat_id] = history

    return history


def create_dict_from_message(message: Message):
    text = message.text.encode('utf-8').decode()
    chat_id = message.chat.id
    msg_id = message.message_id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    unix_timestamp = message.date.timestamp()

    message_data = {
        'text': text,
        'chat_id': chat_id,
        'message_id': msg_id,
        'user_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'date': unix_timestamp,
        'human_readable_date': human_readable_date(unix_timestamp)
    }

    return message_data


def append_message_to_sheet(data_to_save):
    # Select the first sheet in the spreadsheet
    sheet = spreadsheet.get_worksheet_by_id(1170045091)

    # Get the last row index in the sheet
    last_row_index = len(sheet.get_all_values()) + 1

    # Retrieve the header row
    header_row = sheet.row_values(1)

    # Prepare the values to be appended to the sheet
    values = [data_to_save.get(header, "") for header in header_row]

    # Append the values to the last row of the sheet
    sheet.insert_row(values, last_row_index)

    print('Data appended successfully to the Google Spreadsheet.')


async def save_bot_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(f'{bot_data_file_path}.json', 'w') as json_file:
            json.dump(context.bot_data, json_file, indent=4)
        message = f"Bot Data dumped successfully."
        print(message)
    except Exception as e:
        message = f"An error occurred while dumping bot_data {e}"
        print(message)
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=message,
                                   reply_to_message_id=update.message.message_id)


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
