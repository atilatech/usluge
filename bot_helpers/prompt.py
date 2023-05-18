import os

from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain

_template = """Given the following conversation and a follow up question, 
rephrase the follow up question to be a standalone question.
You can assume the question about finding service providers in Montenegro.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

template = """You are a chat bot that helps people find local service providers. 
Examples of service providers include services such as apartment cleaning, painters, plumbers, hairdressers, etc. 
Try your best to help users answer their questions.
You are given the following extracted parts of a long document and a question. Provide a conversational answer.
If you don't know the answer, present some alternatives and say "@IvanKapisoda can help." 
Don't try to make up an answer.
Question: {question}
=========
{context}
=========
Answer in Markdown:"""
QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])


def get_chain(vectors):
    # 'openai_api_key' not needed since it's picked up by default
    # But it's good to be explicit for anyone reading this so they know an API key is required
    llm = OpenAI(temperature=0, openai_api_key=os.environ.get('OPENAI_API_KEY'))
    qa_chain = ChatVectorDBChain.from_llm(
        llm,
        vectors,
        qa_prompt=QA_PROMPT,
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
    )
    return qa_chain
