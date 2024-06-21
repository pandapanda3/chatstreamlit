import streamlit as st
from navigation import make_sidebar
from service.generate_conversation import generate_patient_conversation
from service.mysql import get_connection, get_secret


# get all the chat history of certain session_id
def get_session_chat_detail(session_id):
    value = (session_id,)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT user_role, message FROM chat_records WHERE session_id = %s"
            cursor.execute(sql, value)
            result = cursor.fetchall()
            
            return result
    
    finally:
        connection.close()

# display the chat detail
def display_chat(session_id):
    chat_history = get_session_chat_detail(session_id)
    
    for chat in chat_history:
        user_role, message = chat
        if user_role == "patient":
            st.chat_message("patient").write(message)
        elif user_role == "dentist":
            st.chat_message("dentist").write(message)

make_sidebar()

st.title("💬 History Detail Conversation For a Session")


if "session_id" not in st.session_state:
    st.session_state.session_id = ''
else:
    session_id = st.session_state.session_id
    if session_id != '':
        display_chat(session_id)
    else:
        st.write("No session ID provided.")