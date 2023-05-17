import os
import openai
from bot_helpers.credentials import OPEN_AI_API_KEY

# Set up OpenAI API credentials
openai.api_key = OPEN_AI_API_KEY


def find_service_provider(prompt):
    try:
        # Read the raw text file
        # Get the absolute path of the file within the app's directory
        file_path = os.path.join(os.path.dirname(__file__), 'services.csv')

        # Read the raw text file
        with open(file_path, 'r') as file:
            services_data = file.read()

        # Make the API call to OpenAI
        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt='Prompt: You are a chat bot that helps people find local service providers.'
                   'Examples of service providers include services'
                   ' such as apartment cleaning, painters, plumbers, hairdressers etc.'
                   'Try your best to help user answer their question.'
                   'Reply in English to the following message:'
                   + prompt + '\n\n using the following information' + services_data,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7
        )

        # Process the API response
        print("response.choices", response.choices)
        if response.choices:
            response_text = response.choices[0].text.strip()
            print("response_text", response_text)
            return response_text
        else:
            return None

    except openai.error.RateLimitError as e:
        # Handle RateLimitError
        return str(e)

    except Exception as e:
        # Handle other exceptions
        return str(e)
