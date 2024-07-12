import streamlit as st
import pandas as pd
from navigation import make_sidebar
from service.information_from_mysql import get_users_role, update_users_role
make_sidebar()

# current_user = st.session_state.get('user_info', {"user_id": None, "username": "unknown", "role": "dentist", "authority_role": "normal"})
# be careful about the role
user_info = st.session_state.user_info
authority_role = user_info['authority_role']

if authority_role == 'admin':
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
                    st.write(f"The user :{user_name} will be in the role of {role}")
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
            "student_number": st.column_config.NumberColumn(
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

else:
    st.title("This page is for Admin users only. It is exclusively used for setting roles. You do not have the necessary permissions to access this function.")