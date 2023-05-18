import os
import openai
from bot_helpers.credentials import OPENAI_API_KEY
from bot_helpers.embed import get_vectors
from prompt import get_chain

# Set up OpenAI API credentials
openai.api_key = OPENAI_API_KEY

vectors = get_vectors()


def generate_response(query):
    # TODO: add chat history
    chain = get_chain(vectors)
    response = chain({"question": query, "chat_history": []})["answer"]
    return response
