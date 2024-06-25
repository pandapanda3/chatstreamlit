from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import SequentialChain
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain

def generate_patient_conversation(dentist_input, context="", openai_api_key=""):
    llm_model = "gpt-3.5-turbo"
    
    llm = ChatOpenAI(temperature=0.0, model=llm_model, openai_api_key=openai_api_key)
    first_prompt = ChatPromptTemplate.from_template(
        """
        Generate a conversation with a dentist. The conversation should start with the patient's concern about their dental issue.
        The entire conversation should revolve around inquiring about detailed patient information before performing any actual dental diagnostic procedures.
        This includes asking about the patient's height, weight, allergy history, family hereditary diseases, smoking habits, and other relevant information.
        The generated dialogue should be coherent and natural, with seamless transitions. It should generate only one sentence and wait for the user to respond.
        Patient style: {style}
        Conversation:
        ```{text}```
        """
    )
    second_prompt = ChatPromptTemplate.from_template(
        """
        Continue the conversation with the dentist based on the following context.
        Patient style: {style}
        Conversation:
        ```{text}```
        """
    )
    patient_style = "British English in a patient and respectful tone."
    
    chain_one = SequentialChain(
        chains=[LLMChain(llm=llm, prompt=first_prompt, output_key="patient_initial_response")],
        input_variables=["style", "text"],
        output_variables=["patient_initial_response"]
    )
    
    chain_two = SequentialChain(
        chains=[LLMChain(llm=llm, prompt=second_prompt, output_key="patient_followup_response")],
        input_variables=["style", "text"],
        output_variables=["patient_followup_response"]
    )
    
    if not context:  # initial conversation
        initial_context = "Hi, what can I do for you today?"
        response = chain_one.run(style=patient_style, text=initial_context)
        
    else:
        context = f"{context}\nDentist: {dentist_input}\nPatient:"
        response = chain_two.run(style=patient_style, text=context)
        
    if response.startswith("Patient:"):
        response = response[len("Patient:"):].strip()

    return response

def generate_patient_Symptoms(openai_api_key=""):
    llm_model = "gpt-3.5-turbo"
    llm = ChatOpenAI(temperature=0.9, model=llm_model, openai_api_key=openai_api_key)
    patient_detail = """
            Age: between 20 and 80 years old
            Gender: male or female or other
            Symptoms: Symptoms: common dental issues, including tooth pain, gum bleeding, tooth decay, bad breath, sensitive teeth, swollen gums, tooth discoloration, mouth sores, loose teeth, receding gums etc
            Allergy history: allergies to specific medications, foods, or other substances (please clarify the exact items, not general categories)
            Social habits: whether the patient smokes or drinks alcohol
            Lifestyle habits: whether the patient likes to eat sweets, tooth brushing habits, tooth brushing method

    """
    # prompt template 1: generate information of patient into json format
    first_prompt = ChatPromptTemplate.from_template(
        """
        Please generate information for a patient visiting the dentist in JSON format. The patient's information should include the following:  patient_detail.
         {patient_detail}.
         For Symptoms, include one or two symptoms.
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
    dentist_input = 'I see, thank you for letting me know. Before we proceed with any diagnostic procedures, may I ask for some detailed information about your health?'
    openai_api_key = 'your_openai_api_key'
    
    print(generate_patient_conversation(dentist_input, openai_api_key=openai_api_key))
