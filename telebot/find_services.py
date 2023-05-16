import os

import openai

from telebot.credentials import OPEN_AI_API_KEY

# Set up OpenAI API credentials
openai.api_key = OPEN_AI_API_KEY


def find_service_provider(prompt):
    # Read the raw text file
    # Get the absolute path of the file within the app's directory
    file_path = os.path.join(os.path.dirname(__file__), 'services.csv')

    # Read the raw text file
    with open(file_path, 'r') as file:
        services_data = file.read()

    # Make the API call to OpenAI
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt='Prompt: Reply the following message:' + prompt + '\n\n using the following information' + services_data,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Process the API response
    if response.choices:
        return response.choices[0].text.strip()
    else:
        return None
