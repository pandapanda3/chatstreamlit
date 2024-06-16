import streamlit as st
import pymysql
from navigation import make_sidebar
import bcrypt
import boto3


# the data stores in .streamlit/secrets.toml, it's not a good way to expose it to github. It raises security issues.
def get_connection():
    # db_secrets = st.secrets["mysql"]
    return pymysql.connect(
        host='database-dentist.cx6cggcw84g9.eu-west-2.rds.amazonaws.com',
        user='admin',
        password='kcladmin',
        database='dentist_information',
        port=3306,
        charset='utf8mb4'
    )
    # return {
    #     "RDS_HOST": get_ssm_parameter("RDS_HOST"),
    #     "RDS_PORT": int(get_ssm_parameter("RDS_PORT")),
    #     "RDS_DB": get_ssm_parameter("RDS_DB"),
    #     "RDS_USER": get_ssm_parameter("RDS_USER"),
    #     "RDS_PASSWORD": get_ssm_parameter("RDS_PASSWORD"),
    #     "RDS_CHARSET": get_ssm_parameter("RDS_CHARSET")
    # }

# store the secret data in aws
# def get_ssm_parameter(name):
#     ssm = boto3.client('ssm', region_name='London')
#     secret_data_whole = ssm.get_parameter(Name=name, WithDecryption=True)
#     return secret_data_whole['Parameter']['Value']
    

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
    if authenticate_user(username, password):
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        
        st.switch_page("pages/2Communication.py")
    else:
        st.error("Incorrect username or password")
st.markdown("""
    <style>
    .button-container {
        display: flex;
        justify-content: space-between;
    }
    .button-container > button {
        flex: 1;
        margin: 0 5px;
    }
    </style>
    """, unsafe_allow_html=True)


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
    new_password = st.text_input("New Password", type="password", key="reset_password")
    if st.button("Update Password"):
        update_password(reset_username, new_password)
        st.success("Password updated successfully!")
        st.session_state.show_reset_password_form = False

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
