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
print(f'{type(chat_history_data_df)}, data df is :{chat_history_data_df}')
print(f'{type(chat_history_data)}, data is :{chat_history_data}')

# Display the data in Streamlit
st.data_editor(
    chat_history_data_df,
    column_config={
        "user_name": st.column_config.TextColumn(
            "User Name",
            help="The name of the user",
            width="medium"
        ),
        "chat_count": st.column_config.NumberColumn(
            "The number of question",
            help="The number of chats",
            width="medium"
        ),
        "patient_details": st.column_config.TextColumn(
            "Patient Details",
            help="Details of the patient",
            width="large"
        ),
        "session_id": st.column_config.LinkColumn(
            "Session",
            help="Details of each chat detail",
            width="medium",
            display_text="session_id",
            url="history_page?session_id={session_id}",
        ),
    },
    hide_index=True,
)
