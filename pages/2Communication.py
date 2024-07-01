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

current_user = st.session_state.get('user_info', {"user_id": None, "username": "unknown", "role": "dentist"})
user_id = current_user["user_id"]
user_role = current_user["role"]
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
if 'feedback_key' not in st.session_state:
    st.session_state.feedback_key = 0
    
def increment_message_id():
    st.session_state['message_id'] += 1
    return st.session_state['message_id']

def get_feedback():
    score_mappings = {
        "thumbs": {"👍": 1, "👎": 0},
        "faces": {"😀": 1, "🙂": 0.75, "😐": 0.5, "🙁": 0.25, "😞": 0},
    }
    feedback = streamlit_feedback(
        feedback_type="thumbs",
        score_mapping=score_mappings["thumbs"],
        key=st.session_state.feedback_key
    )
    if feedback:
        st.write(":orange[Component output:]")
        st.write(feedback)
    return feedback

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
    
    context = "\n".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "dentist"])
    patient_response = generate_patient_conversation(dentist_input=dentist_input, context=context,
                                                     openai_api_key=openai_api_key)
    
    st.session_state.messages.append({"role": "patient", "content": patient_response})
    # show the message in the streamlit
    st.chat_message("patient").write(patient_response)

    message_id = increment_message_id()
    insert_message(session_id, user_id, patient_response, "patient", message_id)
    print(f'go to click the checkbox.')
    st.session_state.feedback_key += 1
    feedback = get_feedback()
    
    
    # mark the performance
    # good_on = st.checkbox("Performance is good")
    # print(f'THE VALUE OF GOOD IS :{good_on}')
    # if good_on:
    #     print(f'The message is good: session_id: {session_id}, user_id:{user_id}, message_id:{message_id}')
    #     update_quality_of_each_message(session_id, user_id, message_id, 'good')

    # col1, col2 = st.columns([1, 1])
    # with col1:
    #         with col2:
    #     bad_on = st.toggle("Performance is bad", key='bad:' + str(message_id))
    #     if bad_on:
    # print(f'The message is bad')
    # update_quality_of_each_message(session_id, user_id, message_id, 'bad')
                
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
            
