from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import SequentialChain
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain

def generate_patient_conversation(patient_information, dentist_question, conversation="", openai_api_key=""):
    llm_model = "gpt-3.5-turbo"
    
    llm = ChatOpenAI(temperature=0.9, model=llm_model, openai_api_key=openai_api_key)
    first_prompt = ChatPromptTemplate.from_template(
        """
        Based on the conversation context, summarize the key points in a known_message.
        {{"conversation": {conversation}}}
        Generate a summary message as known_message
        """
    )
    # Chain 1: input=conversation, output=known_message
    chain_one = LLMChain(llm=llm, prompt=first_prompt, output_key="known_message")

    second_prompt = ChatPromptTemplate.from_template(
        """
        You are the patient who is going to see a dentist. The entire conversation should revolve around inquiring about detailed patient information before performing any actual dental diagnostic procedures.
                The generated dialogue should be coherent and natural, with seamless transitions. It should generate only one sentence and wait for the user to respond. The generated dialogue should be coherent and natural, with seamless transitions.
            The information of you is:
            {{"patient_information": {patient_information}}}
            The message that you have already told dentist is:
            {{"known_message": {known_message}}}
            The dentist's question is:
            {{"dentist_question": {dentist_question}}}
            Generate the answer (in one or two sentences) based on dentist_question, then wait for the dentist's response.
            The conversation should be as real as possible. It should not be jargon. You are not expected to tell the dentist all of your information at once.
            You should wait for the dentist to ask you for details.
            Don't repeat the message of known_message. Don't generate the conversation in the role of the dentist. When you finish your answer, wait for the dentist to ask question.
    
        """
    )
    # chain 2
    chain_two = LLMChain(llm=llm, prompt=second_prompt, output_key="answer")
    # Create the SequentialChain
    overall_chain = SequentialChain(
        chains=[chain_one, chain_two],
        input_variables=["conversation", "patient_information", "dentist_question"],
        output_variables=["answer"],
        verbose=True
    )
    # Generate the patient conversation
    response = overall_chain.run({
        "conversation": conversation,
        "patient_information": patient_information,
        "dentist_question": dentist_question
    })

    return response

def generate_patient_Symptoms(openai_api_key=""):
    llm_model = "gpt-3.5-turbo"
    llm = ChatOpenAI(temperature=0.9, model=llm_model, openai_api_key=openai_api_key)
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
        Please generate information for a patient visiting the dentist in JSON format. The patient's information should include the following:  {patient_detail}.
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
    
    print(generate_patient_conversation(dentist_question, openai_api_key=openai_api_key))
