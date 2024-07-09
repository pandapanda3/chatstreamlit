import streamlit as st
from navigation import make_sidebar
from service.mysql import get_connection
import pandas as pd
from st_aggrid.shared import JsCode
from src.agstyler import draw_grid, get_numeric_style_with_precision


st.set_page_config(page_title="History Conversation", layout="wide")
make_sidebar()

# Streamlit App
st.title('History Conversation')
user_info = st.session_state.user_info
user_id = user_info['user_id']


max_table_height = 1000

# Function to generate link
def generate_link(session_id, chat_count):
    return f'<a href="/pages/4History Detail Conversation.py?session_id={session_id}&chat_count={chat_count}" target="_blank">Go to conversation</a>'


#  Fetch data from database
def fetch_chat_history_data(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT chat_count, user_name, patient_details, conversation_score, session_id FROM user_chat_history where user_id =  %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


chat_history_data = fetch_chat_history_data(user_id)

chat_history_data_df = pd.DataFrame(chat_history_data,
                                    columns=["chat_count", "user_name", "patient_details", "conversation_score", "session_id"])
# Function to generate link button
def generate_link_button(session_id, chat_count):
    if st.button(f"Click to view session {chat_count}", key=f"{session_id}-{chat_count}"):
        st.session_state.session_id = session_id
        st.session_state.chat_count = chat_count
        st.switch_page("pages/4History Detail Conversation.py")

# Add link button column to DataFrame
chat_history_data_df['link'] = chat_history_data_df.apply(lambda row: generate_link_button(row['session_id'], row['chat_count']), axis=1)

formatter = {
    "chat_count": ("Chat Count", get_numeric_style_with_precision(0)),
    "user_name": ("User Name", {}),
    "patient_details": ("Patient Details", {"cellStyle": {"textAlign": "center", "whiteSpace": "normal"}}),
    "conversation_score": ("Conversation Score", get_numeric_style_with_precision(0)),
    "session_id": ("Session ID", {}),
    "link": ("Link", {"cellRenderer": JsCode('''function(params) { return params.value; }''')})
}

draw_grid(chat_history_data_df, max_height=max_table_height, formatter=formatter, fit_columns=True, theme="balham")
#
#
# col1, col2 = st.columns([3, 1])
#
# with col1:
#
#     # Display the data in Streamlit
#     st.data_editor(
#         chat_history_data_df,
#         column_config={
#             "chat_count": st.column_config.NumberColumn(
#                 "The number of chat session",
#                 help="The number of chats",
#                 width="small"
#             ),
#             "user_name": st.column_config.TextColumn(
#                 "User Name",
#                 help="The name of the user",
#                 width="medium"
#             ),
#             "patient_details": st.column_config.TextColumn(
#                 "Patient Details",
#                 help="Details of the patient",
#                 width="large"
#             ),
#             "session_id": st.column_config.NumberColumn(
#                 "Tech Details (IGNORE IT)",
#                 help="Tech Details (forget about it)",
#                 width="small"
#             ),
#         },
#         hide_index=True,
#     )
#
# with col2:
#     # when click the button, jump to another page to get the detail message
#     for index, row in chat_history_data_df.iterrows():
#         session_id = row["session_id"]
#         chat_count = row["chat_count"]
#         if st.button(f"Click me to jump into chat session: {chat_count}", key=chat_count):
#             st.session_state.session_id = session_id
#             st.session_state.chat_count = chat_count
#             st.switch_page("pages/4History Detail Conversation.py")
