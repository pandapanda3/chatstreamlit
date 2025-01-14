from typing import Optional, List
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

class DentistPatientRetriever(BaseRetriever):
    """
    Custom retriever to perform a similarity search and return relevant documents.
    """
    db: Optional[object] = Field(default=None, exclude=True)
    def __init__(self, embedding_function, persist_directory: str):
        super().__init__()  # Initialize BaseRetriever
        self.db = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        Perform a similarity search to retrieve the top k relevant documents.
        """
        return self.db.similarity_search(query, k=3)
