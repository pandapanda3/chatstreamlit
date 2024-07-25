import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document as LangchainDocument
from docx import Document

# Load documents from a directory
def load_docx_from_dir(directory):
    all_document_text = []
    for filename in os.listdir(directory):
        if filename.endswith(".docx"):
            document_path = os.path.join(directory, filename)
            each_document = Document(document_path)
            texts = [para.text for para in each_document.paragraphs if para.text.strip()]
            all_document_text.extend(texts)
    return all_document_text

def store_data(OPENAI_API_KEY):
    
    document_direction = "./chatstreamlit/src/document"
    document_texts = load_docx_from_dir(document_direction)
    
    # Preprocess the text to tag dentist questions and patient answers
    tagged_texts = []
    for text in document_texts:
        if "Dentist:" in text or "Patient:" in text:
            tagged_texts.append(text)
    
    # Wrap text in LangchainDocument objects
    documents = [LangchainDocument(page_content=text) for text in tagged_texts]
    
    # Split the documents into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    split_documents = text_splitter.split_documents(documents)
    # for i, doc in enumerate(split_documents):
    #     print(f"Chunk {i+1}: {doc.page_content}\n")
    #
    # Create embeddings for the documents
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    db = Chroma.from_documents(documents=split_documents, embedding=embeddings)
    retriever = db.as_retriever()
    return retriever

if __name__ == '__main__':
    OPENAI_API_KEY=''
    store_data(OPENAI_API_KEY)
