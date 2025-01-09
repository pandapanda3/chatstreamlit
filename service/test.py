import bs4
import os
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import getpass

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini")

# Load, chunk, and index the contents of the blog
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# Create a vector store from the document splits
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Set up the retriever and prompt
retriever = vectorstore.as_retriever()
prompt = hub.pull("rlm/rag-prompt")

# Function to format documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


print(type(retriever),type(format_docs),type(RunnablePassthrough()))
# Define the RAG chain
rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

# Invoke the chain with a question
response = rag_chain.invoke("What is Task Decomposition?")
print(response)