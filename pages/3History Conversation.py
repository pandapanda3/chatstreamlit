import streamlit as st
from navigation import make_sidebar
from service.information_from_mysql import fetch_chat_history_data
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
role = user_info['role']

# max_table_height = 1000

chat_history_data = fetch_chat_history_data(user_id, role)

chat_history_data_df = pd.DataFrame(chat_history_data,
                                    columns=["session_id", "chat_count", "user_name",  "scenario", "emotion", "patient_details", "conversation_score", "performance_feedback","publish_conversation"])
# # Function to generate link button
# # def generate_link_button(session_id, chat_count):
# #     if st.button(f"Click to view session {chat_count}", key=f"{session_id}-{chat_count}"):
# #         st.session_state.session_id = session_id
# #         st.session_state.chat_count = chat_count
# #         st.switch_page("pages/4History Detail Conversation.py")
# #
# # # Add link button column to DataFrame
# # chat_history_data_df['link'] = chat_history_data_df.apply(lambda row: generate_link_button(row['session_id'], row['chat_count']), axis=1)
# #
# # formatter = {
# #     "chat_count": ("Chat Count", get_numeric_style_with_precision(0)),
# #     "user_name": ("User Name", {}),
# #     "patient_details": ("Patient Details", {"cellStyle": {"textAlign": "center", "whiteSpace": "normal"}}),
# #     "conversation_score": ("Conversation Score", get_numeric_style_with_precision(0)),
# #     "session_id": ("Session ID", {}),
# #     "link": ("Link", {"cellRenderer": JsCode('''function(params) { return params.value; }''')})
# # }
# #
# # draw_grid(chat_history_data_df, max_height=max_table_height, formatter=formatter, fit_columns=True, theme="balham")
# #
# #
# col1, col2 = st.columns([5, 1])
#
# with col1:
#
#     # Display the data in Streamlit
#     st.data_editor(
#         chat_history_data_df,
#         column_config={
#             "session_id": st.column_config.NumberColumn(
#                 "Chat",
#                 help="Tech Details , used for getting chat conversation",
#                 width="small"
#             ),
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
#             "scenario": st.column_config.TextColumn(
#                 "Scenario",
#                 help="The Scenario",
#                 width="medium"
#             ),
#             "emotion": st.column_config.TextColumn(
#                 "Emotion",
#                 help="The emotion of the patient",
#                 width="medium"
#             ),
#             "patient_details": st.column_config.TextColumn(
#                 "Patient Details",
#                 help="Details of the patient",
#                 width="large"
#             ),
#             "conversation_score": st.column_config.NumberColumn(
#                 "Conversation Score",
#                 help="The score of this chat session",
#                 width="small"
#             ),
#             "performance_feedback": st.column_config.TextColumn(
#                 "Performance Feedback",
#                 help="The feedback of the conversation given by lecturer",
#                 width="large"
#             ),
#             "publish_conversation": st.column_config.NumberColumn(
#                 "Publish Conversation",
#                 help="It determines whether this conversation can be viewed by the admin user. 1 represents published, 0 represents private.",
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
#         if st.button(f"Click me to jump into chat session: {session_id}", key=f'{chat_count}_{session_id}'):
#             st.session_state.session_id = session_id
#             st.session_state.chat_count = chat_count
#             print(f'the current session id is {session_id}, chat count is {chat_count}')
#             st.switch_page("pages/4History Detail Conversation.py")
#

# Callback function to handle row selection
def single_row_selection_callback():
    # Set a flag to indicate selection occurred
    st.session_state["row_selected"] = True


# Interactive table with single-row selection
event = st.dataframe(
    chat_history_data_df,
    on_select=single_row_selection_callback,  # Callback when a row is selected
    selection_mode="single-row",  # Enable single-row selection
    hide_index=True,
    column_config={
        "session_id": st.column_config.NumberColumn(
            "Chat",
            help="Tech Details , used for getting chat conversation",
            width="small"
        ),
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
        "scenario": st.column_config.TextColumn(
            "Scenario",
            help="The Scenario",
            width="medium"
        ),
        "emotion": st.column_config.TextColumn(
            "Emotion",
            help="The emotion of the patient",
            width="medium"
        ),
        "patient_details": st.column_config.TextColumn(
            "Patient Details",
            help="Details of the patient",
            width="large"
        ),
        "conversation_score": st.column_config.NumberColumn(
            "Conversation Score",
            help="The score of this chat session",
            width="small"
        ),
        "performance_feedback": st.column_config.TextColumn(
            "Performance Feedback",
            help="The feedback of the conversation given by lecturer",
            width="large"
        ),
        "publish_conversation": st.column_config.NumberColumn(
            "Publish Conversation",
            help="It determines whether this conversation can be viewed by the admin user. 1 represents published, 0 represents private.",
            width="small"
        ),
    },
)

# Retrieve selected rows
selected_rows = event.selection.rows

# Handle page redirection based on selection
if st.session_state.get("row_selected", False):
    st.session_state["row_selected"] = False  # Reset the flag
    if len(selected_rows) > 0:
        # Get session_id from the selected row
        selected_session_id = chat_history_data_df.loc[selected_rows[0], "session_id"]
        print(f'selected_rows[0] is {selected_rows[0]}, chat_history_data_df.loc[selected_rows[0], "session_id"] is {selected_session_id} ')
        
        # Get chat_count (second column value) from the selected row
        selected_chat_count = chat_history_data_df.loc[selected_rows[0], "chat_count"]
        print(
            f'selected_rows[0] is {selected_rows[0]}, chat_history_data_df.loc[selected_rows[0], "chat_count"] is {selected_chat_count} ')
        # Store values in session_state
        st.session_state.session_id = selected_session_id
        st.session_state.chat_count = selected_chat_count
        
        # Redirect to the detail page
        st.switch_page("pages/4History Detail Conversation.py")
