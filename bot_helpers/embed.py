import os
import pickle

from langchain import FAISS
from langchain.document_loaders import CSVLoader
from langchain.embeddings import OpenAIEmbeddings

FILE_DIRECTORY = os.path.dirname(__file__)


def get_vectors():
    # Load the vectors from the pickle file
    with open(f"{FILE_DIRECTORY}/data.pkl", "wb") as f:
        vectors = pickle.load(f)

    return vectors


def save_embeddings():
    file_path = os.path.join(FILE_DIRECTORY, 'data.csv')

    loader = CSVLoader(file_path=file_path, encoding="utf-8", csv_args={
        'delimiter': ','})
    data = loader.load()

    embeddings = OpenAIEmbeddings()
    vectors = FAISS.from_documents(data, embeddings)

    # Save the vectors to a pickle file
    with open(f"{FILE_DIRECTORY}/data.pkl", "wb") as f:
        pickle.dump(vectors, f)


if __name__ == "__main__":
    save_embeddings()
