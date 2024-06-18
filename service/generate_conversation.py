from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import SequentialChain
from langchain.chains import LLMChain


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


if __name__ == '__main__':
    dentist_input = 'I see, thank you for letting me know. Before we proceed with any diagnostic procedures, may I ask for some detailed information about your health?'
    openai_api_key = 'your_openai_api_key'
    
    print(generate_patient_conversation(dentist_input, openai_api_key=openai_api_key))
