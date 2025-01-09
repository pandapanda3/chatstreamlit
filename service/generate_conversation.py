from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import SequentialChain
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import OpenAIEmbeddings
from service.rag import store_data
from langchain_core.runnables import RunnablePassthrough
from service.custom_retriever import DentistPatientRetriever
from langchain_core.output_parsers import StrOutputParser

# using the same model
def define_model(openai_api_key=""):
    llm_model = "gpt-3.5-turbo"
    
    llm = ChatOpenAI(temperature=0.8, model=llm_model, openai_api_key=openai_api_key)
    return llm

# retrive information from document
def retrive_document(prompt, dentist_input, openai_api_key=""):
    llm = define_model(openai_api_key)
    retriever = store_data(openai_api_key)
    document_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("human", "{input}")
        ]
    )

    # Combine documents and retrieved information with llm and document_prompt.
    document_prompt_chain = create_stuff_documents_chain(llm, document_prompt)
    # Combine retriever with document_prompt_chain
    rag_document_prompt_chain = create_retrieval_chain(retriever, document_prompt_chain)
    document_answer = rag_document_prompt_chain.invoke({"input": dentist_input})
    answer = document_answer['answer']
    print(f'The chain is {document_answer}. After retrive the document, the answer is {answer}')
    return answer

# generate the greeting answer
def generate_greeting_conversation(dentist_input, openai_api_key=""):
    search_greeting_prompt = (
        """
        You are a highly skilled retriever tasked with searching for answers related to the user's input question.
        Retrieve the question closest to the current user input, then get the corresponding answer to that question.
        Use the following pieces of retrieved context to create a new answer through imitation.
        Ensure the context retrieved includes both the closest question and its following answer.
        ###
        {context}
        ###
        The output should include only the answer to the retrieved question.
        If you have the retrieved context, please mimic its answer to create a new one.
        If no relevant documents are found, only generate sentences where a patient greets a dentist, responding as the patient.
        """
    )
    answer= retrive_document(search_greeting_prompt, dentist_input, openai_api_key=openai_api_key)
    return answer


# get the relative document base on conversation
def retrive_dentist_patient_document(dentist_input, openai_api_key=""):
    search_medical_information_prompt = (
        """
        You are a highly skilled retriever tasked with searching for the most relevant context of the dentist's input in a conversation.
        Retrieve the most relevant conversation snippet related to the current user input.
        Extract the two sentences before and the two sentences after the user's input to provide the full context.
        ###
        {context}
        ###
        The output of answer should include only the two sentences before the user's input, the user's input itself, and the two sentences after the user's input, in that order.
        The output should include both dentist and patient's response in the document.
        If no relevant documents are found, explain that no relevant context could be retrieved.

        """
    )
    answer = retrive_document(search_medical_information_prompt, dentist_input, openai_api_key=openai_api_key)
    return answer
    

def generate_patient_conversation_without_RAG(patient_information, dentist_question, scenario, emotion, conversation="", openai_api_key=""):
    
    llm = define_model(openai_api_key)
    first_prompt = ChatPromptTemplate.from_template(
        """
        Based on the conversation context, summarize the key points in a known_message.
        Conversation:
        {conversation}
        Generate a summary message as known_message.
        """
    )
    # Chain 1: input=conversation, output=known_message
    chain_one = LLMChain(llm=llm, prompt=first_prompt, output_key="known_message")
    
    # get example from document
    example=retrive_dentist_patient_document(dentist_question, openai_api_key=openai_api_key)
    # example = ""
    second_prompt = ChatPromptTemplate.from_template(
        """
        You are the patient who is going to see a dentist. what you response should base on your personality.
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
        The answer should remove "Patient:"
        
        The information of you is:
        ###
        {patient_information}
        ###
        The message that you have already told dentist is:
        ###
        {known_message}
        ###
        The dentist's question is:
        ###
        {dentist_question}
        The personality of you is:
        ###
        {emotion}
        ###
        The scenario of you is:
        ###
        {scenario}
        ###
        The example is:
        ###
        {example}
        ###
    
        Remember to keep your response relevant to the dentist's question from the patient's perspective.
        """
    )
    # chain 2
    chain_two = LLMChain(llm=llm, prompt=second_prompt, output_key="answer")
    # Create the SequentialChain
    overall_chain = SequentialChain(
        chains=[chain_one, chain_two],
        input_variables=["conversation", "patient_information", "dentist_question","emotion","scenario","example"],
        output_variables=["answer"],
        verbose=True
    )
    # Generate the patient conversation
    response = overall_chain.run({
        "conversation": conversation,
        "patient_information": patient_information,
        "dentist_question": dentist_question,
        "emotion": emotion,
        "scenario": scenario,
        "example":example
    })
    print(f'The overall chain is :{overall_chain}')

    return response


# format the docs for RAG
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def Rag_chain(question, prompt, llm, OPENAI_API_KEY, patient_information, known_message, emotion, scenario):
    embedding_function = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    custom_retriever = DentistPatientRetriever(
        embedding_function=embedding_function,
        persist_directory='./chatstreamlit/src/chroma'
    )
    retrieved_docs = custom_retriever._get_relevant_documents(question)
    context = format_docs(retrieved_docs)
    print(f"\nFormatted Context: {context}")
    rag_chain = (
            {
                "context": RunnablePassthrough(),
                "patient_information": RunnablePassthrough(),
                "known_message": RunnablePassthrough(),
                "dentist_question": RunnablePassthrough(),
                "emotion": RunnablePassthrough(),
                "scenario": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
    )
    answer = rag_chain.invoke({
        "context": context,
        "patient_information": patient_information,
        "known_message": known_message,
        "dentist_question": question,
        "emotion": emotion,
        "scenario": scenario
    })
    
    print(f'The answer is {answer}')
    return answer

def generate_patient_conversation_with_RAG(patient_information, dentist_question, scenario, emotion, conversation="", openai_api_key=""):
    llm = define_model(openai_api_key)
    prompt = """You are the patient who is going to see a dentist. what you response should base on your personality.
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
        The answer should remove "Patient:"

        The information of you is:
        ###
        {patient_information}
        ###
        The message that you have already told dentist is:
        ###
        {known_message}
        ###
        The dentist's question is:
        ###
        {dentist_question}
        ###
        The personality of you is:
        ###
        {emotion}
        ###
        The scenario of you is:
        ###
        {scenario}
        ###

        Remember to keep your response relevant to the dentist's question from the patient's perspective.
        """
    prompt_template = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(prompt)
    ])
    response = Rag_chain(
        question=dentist_question,
        prompt=prompt_template,
        llm=llm,
        OPENAI_API_KEY=openai_api_key,
        patient_information=patient_information,
        known_message=conversation,
        emotion=emotion,
        scenario=scenario
    )
    return response
    
def generate_patient_Symptoms(openai_api_key=""):
    llm = define_model(openai_api_key)
    patient_detail = """
            Age: between 20 and 80 years old
            Gender: male or female or other
            Symptoms: common dental issues, including tooth pain, gum bleeding, tooth decay, bad breath, sensitive teeth, swollen gums, tooth discoloration, mouth sores, loose teeth, receding gums etc
            Allergy history: allergies to specific medications, foods, or other substances (please clarify the exact items, not general categories)
            Social habits: whether the patient smokes or drinks alcohol
            Lifestyle habits: whether the patient likes to eat sweets, tooth brushing habits, tooth brushing method

    """
    # prompt template 1: generate information of patient into json format
    first_prompt = ChatPromptTemplate.from_template(
        """
        Please generate information for a patient visiting the dentist in JSON format. The patient's information should include the following: ### {patient_detail} ###.
        For Age, Randomly select a value within a given age range, not just the middle value.
        For Symptoms, include one or two symptoms. briefly describe the symptoms without jargon.
        For Allergy history, it can be either "no allergy" or one specific allergy.
        Only generate the information within patient_detail, without replying to any other irrelevant information.
        patient_detail: {patient_detail}
        """
    )

    # Chain 1
    chain_one = LLMChain(llm=llm, prompt=first_prompt)
    
    # prompt template 2: extract key information and output into str.
    second_prompt = ChatPromptTemplate.from_template(
        """
        For the following text, extract the key information. Format the output with the keys, don't response in json type.
        Patient information:
    text: {text}
        """
    )
    # chain 2
    chain_two = LLMChain(llm=llm, prompt=second_prompt)
    overall_simple_chain = SimpleSequentialChain(chains=[chain_one, chain_two],
                                                 verbose=True
                                                 )
    patient_information = overall_simple_chain.run(patient_detail)
    
    return patient_information
    

if __name__ == '__main__':
    dentist_question = 'I see, thank you for letting me know. Before we proceed with any diagnostic procedures, may I ask for some detailed information about your health?'
    openai_api_key = 'your_openai_api_key'
    