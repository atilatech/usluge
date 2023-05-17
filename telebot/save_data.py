from datetime import datetime

import gspread
import pytz
from telegram import Message

from telebot.credentials import GOOGLE_SERVICE_ACCOUNT_CREDENTIALS

USLUGE_USERS_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16e70m-8SeM1F2suA7rOunico2ASH5xEa_KwdeFbeqMA" \
                               "/edit#gid=0"

# Authenticate using the loaded credentials
gc = gspread.service_account_from_dict(GOOGLE_SERVICE_ACCOUNT_CREDENTIALS)

# Open the Google Spreadsheet by its URL
spreadsheet = gc.open_by_url(USLUGE_USERS_SPREADSHEET_URL)

UPDATE_ID_WORKSHEET_NAME = 'update_id'

UPDATE_ID_WORKSHEET = spreadsheet.worksheet(UPDATE_ID_WORKSHEET_NAME)


def is_repeated_update(update_id):
    previous_update_id = UPDATE_ID_WORKSHEET.acell('A1').value
    print('update_id', update_id)
    print('previous_update_id', previous_update_id)

    if update_id <= int(previous_update_id):
        return True
    return False


# Function to update the latest update_id
def update_latest_update_id(update_id):
    UPDATE_ID_WORKSHEET.update('A1', str(update_id))


def save_message(message: Message):
    dict_message = create_dict_from_message(message)
    append_dict_to_sheet(dict_message)
    return dict_message


def save_message_response(response, message):
    if not hasattr(message, "chat") or not hasattr(message, "message_id"):
        raise ValueError("Invalid message object")

    # Select the first sheet in the spreadsheet
    sheet = spreadsheet.get_worksheet(0)

    try:
        # Find the column index of the "chat_id" and "message_id" columns
        header_row = sheet.row_values(1)
        chat_id_index = header_row.index("chat_id") + 1
        message_id_index = header_row.index("message_id") + 1
        response_index = header_row.index("response") + 1

        # Search for a matching row based on chat_id and message_id
        matching_row = None
        for i, row in enumerate(sheet.get_all_values()[1:], start=2):
            if row[chat_id_index - 1] == str(message.chat.id) and row[message_id_index - 1] == str(message.message_id):
                # Update the response column with the new response
                sheet.update_cell(i, response_index, response)
                matching_row = row
                break

        return matching_row
    except gspread.exceptions.CellNotFound:
        print("No matching row found")
        return None
    except gspread.exceptions.APIError as e:
        # Handle API error
        print("API error occurred:", str(e))
        return None


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

    print('message_data', message_data)

    return message_data


def append_dict_to_sheet(data_to_save):
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

    append_dict_to_sheet(data)
