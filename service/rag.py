import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document as LangchainDocument
from docx import Document
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationSummaryMemory
from langchain.prompts import PromptTemplate
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever
from langsmith import traceable
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# Load documents from a directory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from service.custom_retriever import DentistPatientRetriever
from dotenv import load_dotenv
import os


def load_docx_from_dir(directory):
    all_document_text = []
    for filename in os.listdir(directory):
        if filename.endswith(".docx"):
            document_path = os.path.join(directory, filename)
            each_document = Document(document_path)
            texts = [para.text for para in each_document.paragraphs if para.text.strip()]
            all_document_text.extend(texts)
    return all_document_text


def split_conversations_into_chunks(document_texts, group_size=3):
    """
    Split conversations into chunks where each chunk contains `group_size` groups
    of Dentist and Patient conversations.
    """
    chunks = []
    current_chunk = []
    group_count = 0
    
    for line in document_texts:
        # Add the line to the current chunk
        current_chunk.append(line)
        
        # Check if the line is a Dentist or Patient line
        if "Dentist:" in line or "Patient:" in line:
            group_count += 0.5  # Count each line as half a group
        
        # Once group_count reaches group_size, create a new chunk
        if group_count >= group_size:
            chunk_content = "\n".join(current_chunk)
            chunks.append(LangchainDocument(page_content=chunk_content))
            current_chunk = []  # Reset current chunk
            group_count = 0  # Reset group count
    
    # Add remaining lines as the last chunk
    if current_chunk:
        chunk_content = "\n".join(current_chunk)
        chunks.append(LangchainDocument(page_content=chunk_content))
    
    return chunks

def store_data(OPENAI_API_KEY):
    
    document_direction = "./chatstreamlit/src/document"
    document_texts = load_docx_from_dir(document_direction)

    # Split documents into conversational chunks
    split_documents = split_conversations_into_chunks(document_texts, group_size=3)

    # Print the chunks for debugging
    for i, doc in enumerate(split_documents):
        print(f"Chunk {i + 1}: {doc.page_content}\n")

    # Create embeddings for the documents
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")
    db = Chroma.from_documents(documents=split_documents, embedding=embeddings,
                               persist_directory='./chatstreamlit/src/chroma')
    retriever = db.as_retriever()

    print(f'Finished storing data. Retriever: {retriever}')
    return retriever

# def rertrive_data(query, OPENAI_API_KEY, persist_directory):
#     embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
#     db = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
#     # Set up the retriever using max marginal relevance (MMR) search
#     # This limits the number of documents returned to 3 (k=3)
#     retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 3})
#     llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
#     # Create an LLM-based filter to refine retrieved documents
#     llm_filter = LLMChainFilter.from_llm(llm)
#     # Combine the base retriever and LLM filter into a Contextual Compression Retriever
#     # This enhances the relevance of documents by filtering irrelevant content
#     compression_retriever = ContextualCompressionRetriever(
#         base_compressor=llm_filter, base_retriever=retriever
#     )
#
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=compression_retriever,
#         return_source_documents=True
#     )
#     response = qa_chain(query)
#     print(f'The response is {response}')
#
#     return response['result']

@traceable
def rertrive_data(query, OPENAI_API_KEY, persist_directory):
    embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    # Initialize custom retriever
    custom_retriever = DentistPatientRetriever(
        embedding_function=embedding_function,
        persist_directory=persist_directory
    )
    
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
    # Create an LLM-based filter to refine retrieved documents
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=custom_retriever,
        return_source_documents=True
    )
    response = qa_chain(query)
    print(f'The response is {response}')
    
    return response['result']

def retrive_memory_and_prompt(question,OPENAI_API_KEY):
    llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
    memory = ConversationSummaryMemory(
        llm=llm,
        memory_key="chat_history",
        return_messages=True,
        max_token_limit=3600,
        output_key="result"
    )
    print(memory)
    embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    template = """You are the patient who is going to see a dentist. what you response should base on your personality.
        The conversation will base on scenario. If the message has been told (known_message) to the dentist,
        and when the dentist repeat again the question, you should explain in detail for your previous response.
        When the dentist asks if you have any questions, you might want to inquire about the treatment plan,
        including the duration, specific procedures, and pain management options. Additionally, ask about post-procedure care,
        such as recovery time and any dietary or activity restrictions. Finally, discuss preventive measures,
        follow-up arrangements, and cost and insurance coverage.
        Only respond to the dentist's question without including any unrelated content (in several sentences).
        The entire conversation should revolve around inquiring about detailed patient information before performing any actual dental diagnostic procedures.
        The generated dialogue should be coherent and natural, with seamless transitions.
        As the patient visiting a dentist, follow the scenario below to answer the dentist's question in a few sentences from the patient's perspective.
        It should generate only several sentences and wait for the dentist to respond.
        Remember to keep your response relevant to the dentist's question from the patient's perspective.
    {context}
    Question: {question}
    patient's Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template, )

    
    
    qa_chain = RetrievalQA.from_chain_type(llm,
                                           retriever=vectordb.as_retriever(),
                                           return_source_documents=True,
                                           memory=memory,
                                           output_key="result",
                                           chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})

    result = qa_chain({"query": question})
    response=result["result"]
    print(f'the response is {response}')

    memory_contents = memory.load_memory_variables({})
    print("\nCurrent Memory Contents:")
    print(memory_contents["chat_history"])
    
    return response

# format the docs
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def Rag_chain(question,prompt, llm, OPENAI_API_KEY):
    embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    # vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
    # retriever = vectordb.as_retriever()
    custom_retriever = DentistPatientRetriever(
        embedding_function=embedding_function,
        persist_directory=persist_directory
    )
    rag_chain = (
            {"context": custom_retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    answer = rag_chain.invoke(question)

    
    print(f'The answer is {answer}')
    return answer

if __name__ == '__main__':
    persist_directory='./chatstreamlit/src/chroma'
    load_dotenv()
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    
    # retriever=store_data(OPENAI_API_KEY)
    question='Is there anything you not clear and want to ask me today?'
    # response = rertrive_data(question, OPENAI_API_KEY, persist_directory)
    # print(response)
    # question_list=['And how have you been feeling?',
    #                'Has someone come with you? I mean you can call the attendant in.',
    #                'The results have come back. Well, I am afraid the news today is not very good for you. The biopsy confirmed that the lesion on your right buccal mucosa is grade 3 squamous cell carcinoma which is a type of oral cancer.',
    #                'Yes, I am afraid so. The biopsy has confirmed it.']
    # for question in question_list:
    #     print(f' the qustion is {question}')
    #     response=retrive_memory_and_prompt(question, OPENAI_API_KEY)
    llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
    prompt="""You are the patient who is going to see a dentist. what you response should base on your personality.
        The conversation will base on scenario. If the message has been told (known_message) to the dentist,
        and when the dentist repeat again the question, you should explain in detail for your previous response.
        When the dentist asks if you have any questions, you might want to inquire about the treatment plan,
        including the duration, specific procedures, and pain management options. Additionally, ask about post-procedure care,
        such as recovery time and any dietary or activity restrictions. Finally, discuss preventive measures,
        follow-up arrangements, and cost and insurance coverage.
        Only respond to the dentist's question without including any unrelated content (in several sentences).
        The entire conversation should revolve around inquiring about detailed patient information before performing any actual dental diagnostic procedures.
        The generated dialogue should be coherent and natural, with seamless transitions.
        As the patient visiting a dentist, follow the scenario below to answer the dentist's question in a few sentences from the patient's perspective.
        It should generate only several sentences and wait for the dentist to respond.
        Remember to keep your response relevant to the dentist's question from the patient's perspective.
    {context}
    Question: {question}
    patient's Answer:"""
    prompt_template = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(prompt)
    ])
    response = Rag_chain(question,prompt_template, llm, OPENAI_API_KEY)
