import streamlit as st
from navigation import make_sidebar
from service.mysql import get_connection
import pandas as pd

st.set_page_config(page_title="History Conversation", layout="wide")
make_sidebar()

# Streamlit App
st.title('History Conversation')
user_info = st.session_state.user_info
user_id = user_info['user_id']


#  Fetch data from database
def fetch_chat_history_data(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT chat_count, user_name, patient_details, session_id FROM user_chat_history where user_id =  %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


chat_history_data = fetch_chat_history_data(user_id)

chat_history_data_df = pd.DataFrame(chat_history_data,
                                    columns=["chat_count", "user_name", "patient_details", "session_id"])


col1, col2 = st.columns([3, 1])

with col1:

    # Display the data in Streamlit
    st.data_editor(
        chat_history_data_df,
        column_config={
            "chat_count": st.column_config.NumberColumn(
                "The number of chat session",
                help="The number of chats",
                width="small"
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
            "session_id": st.column_config.NumberColumn(
                "Tech Details (IGNORE IT)",
                help="Tech Details (forget about it)",
                width="small"
            ),
        },
        hide_index=True,
    )

with col2:
    # when click the button, jump to another page to get the detail message
    for index, row in chat_history_data_df.iterrows():
        session_id = row["session_id"]
        chat_count = row["chat_count"]
        if st.button(f"Click me to jump into chat session: {chat_count}", key=chat_count):
            st.session_state.session_id = session_id
            st.session_state.chat_count = chat_count
            st.switch_page("pages/4History Detail Conversation.py")