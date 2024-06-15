import streamlit as st
import pymysql
from navigation import make_sidebar
import bcrypt

db_secrets = st.secrets["mysql"]


def get_connection():
    return pymysql.connect(
        host=db_secrets["RDS_HOST"],
        user=db_secrets["RDS_USER"],
        password=db_secrets["RDS_PASSWORD"],
        database=db_secrets["RDS_DB"],
        port=db_secrets["RDS_PORT"],
        charset=db_secrets["RDS_CHARTSET"]
    )


def authenticate_user(username, password):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT password FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                stored_password = result[0]
                # The password will be encrypted
                return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            return False
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


make_sidebar()

st.title("Welcome to The Platform")

st.write("Please log in to continue.")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Log in", type="primary"):
    if authenticate_user(username, password):
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        
        st.switch_page("pages/2Communication.py")
    else:
        st.error("Incorrect username or password")
