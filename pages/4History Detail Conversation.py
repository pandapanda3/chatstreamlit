import streamlit as st
from navigation import make_sidebar
from service.information_from_mysql import get_session_chat_detail, get_patient_symptoms_detail, \
    insert_performance_feedback


# display the chat detail
def display_chat(session_id):
    chat_history = get_session_chat_detail(session_id)
    
    for chat in chat_history:
        user_role, message, quality = chat
        
        if quality:
            print(f'inside the quality: {quality}')
            if quality == 'good':
                message = message + ' 👍'
            else:
                message = message + ' 👎'
        if user_role == "patient":
            st.chat_message("patient").write(message)
        elif user_role == "dentist":
            st.chat_message("dentist").write(message)


make_sidebar()

st.title("💬 History Detail Conversation For a Session")
st.text('If the page is blank, please go the the History Conversation page to choose a session.')
print('*' * 100)
if "session_id" not in st.session_state:
    st.session_state.session_id = ''
else:
    session_id = st.session_state.session_id
    user_info = st.session_state.user_info
    user_id = user_info['user_id']
    role = user_info['role']
    if session_id != '':
        display_chat(session_id)
        print(f'the session ID in history detail conversation is {session_id}')
        with st.sidebar:
            patient_symptoms_detai_result = get_patient_symptoms_detail(session_id)
            for result in patient_symptoms_detai_result:
                print(f'patient_symptoms_detai_result is {patient_symptoms_detai_result}')
                patient_symptoms, conversation_score, performance_feedback = result
                print(f'patient_symptoms: {patient_symptoms}, conversation_score :{conversation_score}')
                if patient_symptoms:
                    st.markdown(patient_symptoms)
                if conversation_score:
                    st.markdown(f"The quality of this conversation is: {conversation_score}")
                else:
                    st.markdown(f"The quality of this conversation is: NULL")
                # display feedback
                if role == 'admin':
                    performance = st.text_area(placeholder="Please input the feedback of the user's performance. ", value=performance_feedback, label="Please input feedback")
                    print(f'The input feedback is {performance}')
                    insert_performance_feedback(performance_feedback, session_id)
                else:
                    st.write_stream(performance_feedback)
    else:
        st.write("No session ID provided.")
