import streamlit as st
from navigation import make_sidebar
from service.generate_conversation import generate_patient_conversation
from service.mysql import get_connection, get_secret


# insert message
def insert_message(session_id, user_id, message, user_role):
    
    value = (session_id, user_id, message, user_role)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO chat_records (session_id, user_id, message, user_role) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, value)
            connection.commit()
            
    finally:
        connection.close()


# get the largest number of chat_count of the user
def get_largest_chat_number(user_id):
    value = (user_id)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT MAX(chat_count) AS max_chat_count FROM user_chat_history WHERE user_id = %s"
            cursor.execute(sql, value)
            result = cursor.fetchone()
            max_chat_count = result[0] if result else 0
            print(f'The max chat number is :{max_chat_count}')
            return max_chat_count
    
    finally:
        connection.close()

# insert user_chat_history
def insert_user_chat_history(user_id, user_name, chat_count, patient_details):
    value = (user_id, user_name, chat_count, patient_details)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO user_chat_history (user_id, user_name, chat_count, patient_details) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, value)
            connection.commit()
    
    finally:
        connection.close()
        
# generate session id
def generate_session_id():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(session_id) FROM chat_records")
            result = cursor.fetchone()
            max_session_id = result[0] if result[0] is not None else 0
            return max_session_id + 1
    finally:
        connection.close()


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

if 'session_id' not in st.session_state or st.session_state['session_id'] is None:
    st.session_state['session_id'] = generate_session_id()

session_id = st.session_state['session_id']

if "messages" not in st.session_state or not st.session_state["messages"]:
    st.session_state["messages"] = [{"role": "patient", "content": "Hello, doctor. How are you today?"}]

for msg in st.session_state.messages:
    if msg["role"] == "patient":
        st.chat_message("patient").write(msg["content"])
    else:
        st.chat_message("dentist", is_user=True).write(msg["content"])

if dentist_input := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    # Check if there is only one message in the session state
    if 'messages' in st.session_state and len(st.session_state.messages) == 1:
        max_chat_count = get_largest_chat_number(user_id)
        insert_user_chat_history(user_id, username, max_chat_count + 1, f'patient for {username}')

    st.session_state.messages.append({"role": "dentist", "content": dentist_input})
    # show the message in the streamlit
    st.chat_message("dentist", is_user=True).write(dentist_input)
    # save the conversation
    insert_message(session_id, user_id, dentist_input, "dentist")
    
    
    context = "\n".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "dentist"])
    patient_response = generate_patient_conversation(dentist_input=dentist_input, context=context, openai_api_key=openai_api_key)

    st.session_state.messages.append({"role": "patient", "content": patient_response})
    # show the message in the streamlit
    st.chat_message("patient").write(patient_response)
    insert_message(session_id, user_id, patient_response, "patient")


