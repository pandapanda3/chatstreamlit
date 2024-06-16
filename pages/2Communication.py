from openai import OpenAI
import streamlit as st
from navigation import make_sidebar
from service.mysql import get_connection

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

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

st.title("💬 Communication")

current_user = st.session_state.get('user_info', {"user_id": None, "username": "unknown", "role": "dentist"})
user_id = current_user["user_id"]
user_role = current_user["role"]

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = generate_session_id()

session_id = st.session_state['session_id']



if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "I have a headache."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    # insert the data
    insert_message(session_id, user_id, prompt, "dentist")
    
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    insert_message(session_id, user_id, msg, "patient")


