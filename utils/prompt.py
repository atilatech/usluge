import os
import pickle

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

_template = """Given the following conversation and a follow-up question, 
rephrase the follow-up question to be a standalone question.
You can assume the question is about finding service providers in Montenegro.

Chat History:
{chat_history}
Follow-Up Input: {question}
Standalone Question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

template = """You are a chatbot that helps people find local service providers. 
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

FILE_DIRECTORY = os.path.dirname(__file__)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


def get_vectors():
    # Load the vectors from the pickle file
    with open(f"{FILE_DIRECTORY}/data.pkl", "rb") as f:
        vectors = pickle.load(f)

    return vectors


prompt_template = """You are a chatbot that helps people find local service providers. 
Examples of service providers include services such as apartment cleaning, painters, plumbers, hairdressers, etc. 
Try your best to help users answer their questions.
Use the following pieces of context to answer the question at the end.

Reply in the same language that the question is asked.
For example, if the question is in English, reply in English. If the answer is in Serbian, reply in Serbian.

Answer the question using the context. Provide a concise, friendly and conversational answer.
Don't try to make up an answer.
Question: {question}

Context:
=========
{context}
=========
Answer in Markdown:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["question", "context"]
)


def get_conversation_chain():
    conversation_template = """You are a chatbot that helps people book local taxis.
    
    {chat_history}
    Human: {human_input}
    Chatbot:"""

    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"],
        template=conversation_template
    )
    llm_chain = LLMChain(
        llm=OpenAI(),
        prompt=prompt,
        verbose=True,
        memory=memory,
    )
    return llm_chain


def get_chain(vectors):
    # Replace BaseRetriever with the appropriate retriever class
    combine_docs_chain_kwargs = {"prompt": PROMPT}
    llm = OpenAI(temperature=0, openai_api_key=os.environ.get('OPENAI_API_KEY'))
    qa_chain = ConversationalRetrievalChain.from_llm(llm,
                                                     chain_type="stuff",
                                                     retriever=vectors.as_retriever(),
                                                     combine_docs_chain_kwargs=combine_docs_chain_kwargs)
    return qa_chain