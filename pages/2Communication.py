import streamlit as st
from navigation import make_sidebar
from service.generate_conversation import generate_patient_conversation, generate_patient_Symptoms
from service.information_from_mysql import generate_session_id, get_largest_chat_number, \
    insert_user_chat_history, insert_message, update_user_chat_history_quality, update_quality_of_each_message
from service.mysql import get_secret
from streamlit_feedback import streamlit_feedback

make_sidebar()
# get openai_key
secret_values = get_secret()
openai_api_key = secret_values['openai_api_key']
if openai_api_key == '':
    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

st.title("💬 Communication")

current_user = st.session_state.get('user_info', {"user_id": None, "username": "unknown", "role": "dentist", "authority_role": "normal"})
user_id = current_user["user_id"]
# user_role = current_user["role"]
username = current_user["username"]
print(f'st.session_state is :{st.session_state}')

if "messages" not in st.session_state or not st.session_state["messages"]:
    st.session_state["messages"] = [{"role": "patient", "content": "Hello, doctor. How are you today?"}]

# generate session id from chat_records
if 'session_id' not in st.session_state or st.session_state['session_id'] is None:
    st.session_state['session_id'] = generate_session_id()
if 'patient_symptoms' not in st.session_state:
    st.session_state['patient_symptoms'] = ''
if 'message_id' not in st.session_state:
    st.session_state['message_id'] = 0
if 'conversation_score' not in st.session_state:
    st.session_state['conversation_score'] = ''

    
def increment_message_id():
    st.session_state['message_id'] += 1
    return st.session_state['message_id']

# get feed back for the generation of the model
def get_feedback():
    message_id = st.session_state.message_id
    feedback_information = st.session_state.feedback
    print(f'the feedback information is {feedback_information}')
    feedback_information_score = feedback_information.get('score', None)

    if feedback_information_score:
        st.toast(":red[ Feedback received! ]", icon="🔥")
        print(f'After the  feed back, the session state is :{st.session_state} ')
        feedback_score = st.session_state.feedback['score']
        
        if feedback_score == '👍':
            print(f'insert good')
            update_quality_of_each_message(session_id, user_id, message_id, 'good')
        elif feedback_score == '👎':
            update_quality_of_each_message(session_id, user_id, message_id, 'bad')
            print(f'insert bad')
    else:
        st.toast(":red[ Please provide feedback by clicking thumbs up or thumbs down. ]", icon="⚠️")


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

session_id = st.session_state['session_id']

dentist_input = st.chat_input("Input your question! ",)
if dentist_input:
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    # Check if there is only one message in the session state
    if 'messages' in st.session_state and len(st.session_state.messages) == 1:
        # get the largest chat number of a person
        max_chat_count = get_largest_chat_number(user_id)
        if not max_chat_count:
            max_chat_count = 0
        chat_count = max_chat_count + 1
        # generate the symptoms of patient
        patient_Symptoms = generate_patient_Symptoms(openai_api_key)
        st.session_state['patient_symptoms'] = patient_Symptoms
        insert_user_chat_history(user_id, username, chat_count, patient_Symptoms, session_id)

        
    st.session_state.messages.append({"role": "dentist", "content": dentist_input})
    # show the message in the streamlit
    st.chat_message("dentist").write(dentist_input)

    # save the conversation
    message_id = increment_message_id()
    insert_message(session_id, user_id, dentist_input, "dentist", message_id)
    
    # gather all the information that patient has told dentist
    context = "\n".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "dentist"])
    # generate the answer of patient
    print(f"In generating the patient's answer, symptoms is {st.session_state['patient_symptoms']}, dentist_input is {dentist_input}, conversation is {context}")
    patient_response = generate_patient_conversation(st.session_state['patient_symptoms'], dentist_input, conversation=context, openai_api_key=openai_api_key)
    
    st.session_state.messages.append({"role": "patient", "content": patient_response})
    # show the message in the streamlit
    st.chat_message("patient").write(patient_response)

    message_id = increment_message_id()
    insert_message(session_id, user_id, patient_response, "patient", message_id)
    
    # get feedback
    with st.form('form'):
        streamlit_feedback(feedback_type="thumbs", align="flex-end", key='feedback')
        st.form_submit_button('Save feedback', on_click=get_feedback, use_container_width = True)
    

# if it has already generate the patient_information, show it in the sidebar
if len(st.session_state.messages) > 1:
    print(f'communication the last one, session id is :{session_id}, session state is {st.session_state}')
    with st.sidebar:
        formatted_symptoms=st.session_state['patient_symptoms'].replace('\n', '<br>')
        st.markdown(formatted_symptoms, unsafe_allow_html=True)
        
        conversation_score = st.number_input("How would you rate the quality of this conversation?", min_value=0, max_value=100, step=1, format="%d", value=None, placeholder="Number between 0 to 100")
        
        if conversation_score is not None and conversation_score != st.session_state['conversation_score']:
            st.write("The quality of this conversation is ", conversation_score)
            chat_count_number = get_largest_chat_number(user_id)
            update_user_chat_history_quality(user_id, username, chat_count_number, conversation_score)
            st.session_state['conversation_score'] = conversation_score

