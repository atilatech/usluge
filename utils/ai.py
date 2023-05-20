from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from utils.utils import request_requirements

chat = ChatOpenAI(temperature=0)

ai_true_key = 'ai_true'


def check_enough_info_to_make_request(request):
    template = "Your job is to let the user know if the message has enough information to get a driver." \
               "Does the following message have enough information to book a driver?" \
               f"If there is enough information, include '{ai_true_key}' in your response. Otherwise,"\
               f"The following 4 pieces of information is required to book a driver: {request_requirements}."
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
