import streamlit as st
from navigation import make_sidebar
import bcrypt
from service.mysql import get_connection


def authenticate_user(username, password, student_number):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, password, role FROM users WHERE username = %s and student_number = %s"
            cursor.execute(sql, (username, student_number))
            result = cursor.fetchone()
            if result:
                user_id, stored_password, role = result
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    return {"user_id": user_id, "username": username, "role": role}
            return None
    finally:
        connection.close()


def create_user(username, password, role='normal'):
    connection = get_connection()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, role))
            connection.commit()
    finally:
        connection.close()

def update_password(username, new_password, student_number):
    connection = get_connection()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET password = %s WHERE username = %s AND student_number = %s"
            cursor.execute(sql, (hashed_password, username, student_number))
            connection.commit()
    finally:
        connection.close()
        

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