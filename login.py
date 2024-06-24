import streamlit as st
from navigation import make_sidebar
import bcrypt
from service.mysql import get_connection


def authenticate_user(username, password):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, password, role FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
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

def update_password(username, new_password):
    connection = get_connection()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET password = %s WHERE username = %s"
            cursor.execute(sql, (hashed_password, username))
            connection.commit()
    finally:
        connection.close()
        

make_sidebar()

st.title("Welcome to The Platform")

st.write("Please log in to continue.")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Log in", type="primary"):
    user_info = authenticate_user(username, password)
    if user_info:
        st.session_state.logged_in = True
        st.session_state.user_info = user_info
        st.session_state['session_id'] = None
        st.session_state['messages'] = []
        st.success("Logged in successfully!")
        st.switch_page("pages/2Communication.py")
    else:
        st.error("Incorrect username or password")
     


def show_create_account_form():
    st.write("## Create an Account")
    new_username = st.text_input("New Username", key="new_username")
    new_password = st.text_input("New Password", type="password", key="new_password")
    if st.button("Register"):
        create_user(new_username, new_password)
        st.success("Account created successfully!")
        st.session_state.show_create_account_form = False

def show_reset_password_form():
    st.write("## Reset Password")
    reset_username = st.text_input("Username for Password Reset", key="reset_username")
    new_password = st.text_input("New Password", type="password", key="new_password")
    new_password_confirm = st.text_input("Confirm New Password", type="password", key="new_password_confirm")
    if st.button("Update Password"):
        if new_password == new_password_confirm:
            update_password(reset_username, new_password)
            st.success("Password updated successfully!")
            st.session_state.show_reset_password_form = False
        else:
            st.error("Passwords do not match. Please try again.")

if 'show_create_account_form' not in st.session_state:
    st.session_state.show_create_account_form = False

if 'show_reset_password_form' not in st.session_state:
    st.session_state.show_reset_password_form = False

st.markdown('<div class="button-container">', unsafe_allow_html=True)
if st.button("Create an Account"):
    st.session_state.show_create_account_form = True
    st.session_state.show_reset_password_form = False

if st.button("Forgot Password"):
    st.session_state.show_create_account_form = False
    st.session_state.show_reset_password_form = True
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.show_create_account_form:
    show_create_account_form()

if st.session_state.show_reset_password_form:
    show_reset_password_form()
