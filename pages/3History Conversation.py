import streamlit as st
from navigation import make_sidebar
from service.information_from_mysql import fetch_chat_history_data
import pandas as pd

st.set_page_config(page_title="History Conversation", layout="wide")
make_sidebar()

# Streamlit App
st.title('History Conversation')
st.write("When you hover over the first column on the left, a radio button will appear. Clicking this radio button will navigate to the details page for the corresponding conversation.")
user_info = st.session_state.user_info
user_id = user_info['user_id']
role = user_info['role']

chat_history_data = fetch_chat_history_data(user_id, role)

chat_history_data_df = pd.DataFrame(chat_history_data,
                                    columns=["session_id", "chat_count", "user_name",  "scenario", "emotion", "patient_details", "conversation_score", "performance_feedback","publish_conversation"])

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
    height=1000,
    column_config={
        "session_id": st.column_config.NumberColumn(
            "Chat",
            help="Tech Details , used for getting chat conversation"
        ),
        "chat_count": st.column_config.NumberColumn(
            "The number of chat session",
            help="The number of chats"
        ),
        "user_name": st.column_config.TextColumn(
            "User Name",
            help="The name of the user"
        ),
        "scenario": st.column_config.TextColumn(
            "Scenario",
            help="The Scenario"
        ),
        "emotion": st.column_config.TextColumn(
            "Emotion",
            help="The emotion of the patient"
        ),
        "patient_details": st.column_config.TextColumn(
            "Patient Details",
            help="Details of the patient"
        ),
        "conversation_score": st.column_config.NumberColumn(
            "Conversation Score",
            help="The score of this chat session"
        ),
        "performance_feedback": st.column_config.TextColumn(
            "Performance Feedback",
            help="The feedback of the conversation given by lecturer"
        ),
        "publish_conversation": st.column_config.NumberColumn(
            "Publish Conversation",
            help="It determines whether this conversation can be viewed by the admin user. 1 represents published, 0 represents private."
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
