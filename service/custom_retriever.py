from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
import os

class DentistPatientRetriever(BaseRetriever):
    """
    Custom retriever to find dentist's most relevant statement
    based on the user's query and return the patient's response following it.
    """

    # Explicitly declare fields required by pydantic
    db: Chroma = Field()
    embedding_function: OpenAIEmbeddings = Field()
    persist_directory: str = Field()
    if not os.access(persist_directory, os.R_OK | os.W_OK):
        raise PermissionError(f"Persist directory is not accessible: {persist_directory}")

    def __init__(self, embedding_function, persist_directory: str):
        super().__init__()  # Ensure BaseRetriever initialization
        self.embedding_function = embedding_function
        self.persist_directory = persist_directory
        self.db = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    def _get_relevant_documents(self, query: str) -> List[Document]:

        # Step 1: Perform similarity search to retrieve documents
        documents = self.db.similarity_search(query, k=3)
        # documents = self.db.similarity_search_with_score(query, k=3)
        print(f"documents is {documents}.")
        return documents

