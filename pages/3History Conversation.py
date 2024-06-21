import streamlit as st
from navigation import make_sidebar
from service.mysql import get_connection
import pandas as pd

make_sidebar()

# Streamlit App
st.title('History Conversation')
user_info = st.session_state.user_info
user = user_info['username']
user_id = user_info['user_id']


#  Fetch data from database
def fetch_chat_history_data(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT user_name, chat_count, patient_details, session_id FROM user_chat_history where user_id =  %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


chat_history_data = fetch_chat_history_data(user_id)

chat_history_data_df = pd.DataFrame(chat_history_data,
                                    columns=["user_name", "chat_count", "patient_details", "session_id"])

# chat_history_data_df["session_id"] = chat_history_data_df["session_id"].astype(str)

# Display the data in Streamlit
st.data_editor(
    chat_history_data_df,
    column_config={
        "chat_count": st.column_config.NumberColumn(
            "The number of chat session",
            help="The number of chats",
            width="medium"
        ),
        "user_name": st.column_config.TextColumn(
            "User Name",
            help="The name of the user",
            width="medium"
        ),
        "patient_details": st.column_config.TextColumn(
            "Patient Details",
            help="Details of the patient",
            width="large"
        ),
        
    },
    hide_index=True,
)

session_ids = chat_history_data_df["session_id"].tolist()
if "session_id" not in st.session_state:
    st.session_state.session_id = ''
print(f'the session state information: {st.session_state}')
for session_id in session_ids:
    if st.button(f"click me to jump into the detail: {session_id}", key=session_id):
        st.session_state.session_id = session_id
        st.page_link("pages/4History Detail Conversation.py", label="History Detail Conversation")