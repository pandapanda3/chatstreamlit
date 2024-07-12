import streamlit as st
from navigation import make_sidebar
from service.information_from_mysql import authenticate_user, create_user, update_password

make_sidebar()

st.title("Welcome to The Platform")

st.write("Please log in to continue.")

Login, Register, Reset = st.tabs(["Login", "Register", "Reset Password"])

with Login:
    username = st.text_input("Username")
    student_number = st.text_input("Student Number", key='login_student_number')
    password = st.text_input("Password", type="password")
    
    if st.button("Log in"):
        user_info = authenticate_user(username, password, student_number)
        if user_info:
            st.session_state.logged_in = True
            st.session_state.user_info = user_info
            st.session_state['session_id'] = None
            st.session_state['messages'] = []
            st.success("Logged in successfully!")
            st.switch_page("pages/2Communication.py")
        else:
            st.error("Incorrect username or password")
            
with Register:
    new_username = st.text_input("New Username", key="new_username")
    student_number = st.text_input("Student Number", key='Register_student_number')
    new_password = st.text_input("New Password", type="password", key="Register_new_password")
    new_password_confirm = st.text_input("Confirm New Password", type="password", key="Register_new_password_confirm")
    if st.button("Register"):
        create_user(new_username, new_password,student_number)
        st.success("Account created successfully!")
        
        
with Reset:
    reset_username = st.text_input("Username for Password Reset", key="reset_username")
    student_number = st.text_input("Student Number", key='Reset_student_number')
    new_password = st.text_input("New Password", type="password", key="new_password")
    new_password_confirm = st.text_input("Confirm New Password", type="password", key="new_password_confirm")
    if st.button("Update Password"):
        if new_password == new_password_confirm:
            update_password(reset_username, new_password,student_number)
            st.success("Password updated successfully!")
        else:
            st.error("Passwords do not match. Please try again.")