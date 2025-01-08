from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from pydantic import Field


class DentistPatientRetriever(BaseRetriever):
    """
    Custom retriever to find dentist's most relevant statement
    based on the user's query and return the patient's response following it.
    """

    # Explicitly declare fields required by pydantic
    db: Chroma = Field()
    embedding_function: OpenAIEmbeddings = Field()
    persist_directory: str = Field()

    def __init__(self, embedding_function, persist_directory: str):
        """
        Initialize the custom retriever.

        Args:
            embedding_function: The embedding function to compute document embeddings.
            persist_directory (str): Path to the Chroma database directory.
        """
        super().__init__()  # Ensure BaseRetriever initialization
        self.embedding_function = embedding_function
        self.persist_directory = persist_directory
        self.db = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        Retrieve relevant documents using similarity search, then extract
        dentist's statements and following patient's responses.

        Args:
            query (str): User's query.

        Returns:
            List[Document]: A list of relevant documents with extracted content.
        """
        

        # Step 1: Perform similarity search to retrieve documents
        documents = self.db.similarity_search(query, k=3)
        # documents = self.db.similarity_search_with_score(query, k=3)
        print(f"documents is {documents}.")

        
        return documents
