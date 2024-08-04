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

# message display in sidebar
def sidebar_display(name, value):
    if name:
        st.markdown(f"The {name} of this conversation is: {value}")
    else:
        st.markdown(f"The {name} of this conversation is: NULL")
        
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
                patient_symptoms, conversation_score, performance_feedback,scenario,emotion, publish_conversation = result
                print(f'patient_symptoms: {patient_symptoms}, conversation_score :{conversation_score}')
                sidebar_display('scenario', scenario)
                sidebar_display('emotion', emotion)
                if patient_symptoms:
                    st.markdown(patient_symptoms)
                sidebar_display('quality', conversation_score)
                if publish_conversation == 1:
                    st.markdown(f"The conversation has been published!")
                else:
                    st.markdown(f"The conversation is privacy!")
                
                # display feedback
                if role == 'admin':
                    performance = st.text_area(placeholder="Please input the feedback of the user's performance. ", value=performance_feedback, label="Please input feedback")
                    insert_result=insert_performance_feedback(performance, session_id)
                    if insert_result:
                        st.toast(f'The feedback has been submitted! Thank you!')
                else:
                    performance = st.text_area(disabled=True, value=performance_feedback, label="The feedback of user's performance")

    else:
        st.write("No session ID provided.")
