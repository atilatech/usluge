import os
import openai
from utils.credentials import OPENAI_API_KEY
from utils.embed import get_vectors
from utils.prompt import get_chain

# Set up OpenAI API credentials
openai.api_key = OPENAI_API_KEY

vectors = get_vectors()


def generate_response(query):
    # https://python.langchain.com/en/latest/modules/chains/index_examples/chat_vector_db.html
    # If you had multiple loaders that you wanted to combine, you do something like:
    #
    # # loaders = [....]
    # # docs = []
    # # for loader in loaders:
    # #     docs.extend(loader.load())

    chain = get_chain(vectors)
    # TODO: add chat history
    # chat_history = [('<user_question>', '<ai_response>')]
    response = chain({"question": query, "chat_history": []})
    print('response', response)
    return response
