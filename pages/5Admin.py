import streamlit as st
import pandas as pd
from navigation import make_sidebar
from service.information_from_mysql import get_users_role, update_users_role, get_quality, get_conversation_score
import matplotlib.pyplot as plt

make_sidebar()

# be careful about the role
user_info = st.session_state.user_info
role = user_info['role']

if role == 'admin':
    # create a container
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            user_name = st.text_input("user name", placeholder="Please input uer name")
    
        with col2:
            k_number = st.text_input("user number", placeholder="Please input uer number")
            
        
        with col3:
            role = st.selectbox("select the role", ["admin", "normal"])
        all_fields_filled = user_name and k_number and role
        
        with col4:
            if st.button("submit", disabled=not all_fields_filled):
                update_result = update_users_role(user_name, k_number,role)
                if update_result:
                    st.toast(f"The user :{user_name} will be in the role of {role}")
        if not all_fields_filled:
            st.warning("Please fill out all the fields before submitting.")

    users_role = get_users_role()

    users_role_df = pd.DataFrame(users_role,
                                        columns=["username", "student_number", "role"])
    # Display the data in Streamlit
    st.data_editor(
        users_role_df,
        column_config={
            "username": st.column_config.TextColumn(
                "User Name",
                help="The name of the user",
                width="medium"
            ),
            "student_number": st.column_config.TextColumn(
                "The k number of student",
                help="The k number of student",
                width="medium"
            ),
            
            "role": st.column_config.TextColumn(
                "Role",
                help="The role of the user",
                width="medium"
            ),
            
        },
        
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        quality_list=get_quality()
        print(f'The quality_list is{quality_list}')
        quality_list_df = pd.DataFrame(quality_list)
        counts = quality_list_df['quality'].value_counts()
        labels = counts.index.tolist()
        sizes = counts.values.tolist()
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
    with col2:
        conversation_score_list = get_conversation_score()
        print(f'The conversation_score_list is{conversation_score_list}')
        conversation_score_list_df = pd.DataFrame(conversation_score_list)
        score_counts = conversation_score_list_df['conversation_score'].value_counts().sort_index()
        fig, ax = plt.subplots()
        bars = ax.bar(score_counts.index, score_counts.values)
        ax.set_xlabel('Conversation Score')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Conversation Scores')
        ax.bar_label(bars)
        st.pyplot(fig)


else:
    st.title("This page is for Admin users only. It is exclusively used for setting roles. You do not have the necessary permissions to access this function.")