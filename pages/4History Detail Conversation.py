import streamlit as st
from navigation import make_sidebar
from service.information_from_mysql import get_session_chat_detail, get_patient_symptoms_detail

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
st.text('If the page is blank, please go the the History Conversation page to choose a session.')
print('*'*100)
if "session_id" not in st.session_state:
    st.session_state.session_id = ''
else:
    session_id = st.session_state.session_id
    if session_id != '':
        display_chat(session_id)
        print(f'the session ID is {session_id}')
        with st.sidebar:
            patient_symptoms = get_patient_symptoms_detail(session_id)
            if patient_symptoms:
                # each session only has one record
                formatted_symptoms = patient_symptoms[0][0].replace('\n', '<br>')
                st.markdown(formatted_symptoms, unsafe_allow_html=True)
    else:
        st.write("No session ID provided.")