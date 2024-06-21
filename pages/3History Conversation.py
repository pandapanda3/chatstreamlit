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
# print(f'{type(chat_history_data_df)}, data df is :{chat_history_data_df}')
# print(f'{type(chat_history_data)}, data is :{chat_history_data}')
#
# Display the data in Streamlit
st.data_editor(
    chat_history_data_df,
    column_config={
        "chat_count": st.column_config.NumberColumn(
            "The number of question",
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
        "session_id": st.column_config.LinkColumn(
            "Session",
            help="Details of each chat detail",
            width="large",
            display_text="click me to show the detail",
            url="history_page?session_id={session_id}",
        ),
    },
    hide_index=True,
)

# st.dataframe(chat_history_data_df)
#
# for index, row in chat_history_data_df.iterrows():
#     session_id = row["session_id"]
#     if st.button(f"查看会话 {session_id}", key=session_id):
#         st.query_params(session_id=session_id)
#         st.rerun()

# st.write(chat_history_data_df)
# # selected_row = st.selectbox("Select a row to get session_id", chat_history_data_df.columns)
# #
# # # 提取选中行的 session_id
# # session_id = chat_history_data_df.loc[selected_row, "session_id"]
# #
# # # 显示 session_id
# # st.write(f"Selected session_id: {session_id}")
# # st.query_params.session_id = session_id

session_ids = chat_history_data_df["session_id"].tolist()

for session_id in session_ids:
    if st.button(f"click me to jump into the detail: {session_id}", key=session_id):
        st.query_params.session_id = session_id
        st.page_link("pages/4History Detail Conversation.py", label="History Detail Conversation")