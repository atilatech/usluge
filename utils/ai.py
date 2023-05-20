from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from utils.utils import request_requirements

chat = ChatOpenAI(temperature=0)

ai_true_key = 'ai_true'


def check_enough_info_to_make_request(request):
    template = "Your job is to let the user know if the message has enough information to get a driver." \
               "If it does not, let the user know what is missing in a friendly and concise way" \
               f"If there is enough information, include '{ai_true_key}' in your response. Otherwise,"\
               f"Please provide the following: {request_requirements}."
    with get_openai_callback() as cb:
        messages = [
            SystemMessage(content=template),
            HumanMessage(content=request)
        ]
        result = chat(messages)
        print('result', result)
        print(cb)

    print('request, result', request, result)
    return result.content
