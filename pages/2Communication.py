import streamlit as st
from navigation import make_sidebar
from service.generate_conversation import generate_patient_conversation
from service.mysql import get_connection
import boto3
from botocore.exceptions import ClientError

# insert message
def insert_message(session_id, user_id, message, user_role):
    
    value = (session_id, user_id, message, user_role)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO chat_records (session_id, user_id, message, user_role) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, value)
            connection.commit()
            
    finally:
        connection.close()
        
# generate session id
def generate_session_id():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(session_id) FROM chat_records")
            result = cursor.fetchone()
            max_session_id = result[0] if result[0] is not None else 0
            return max_session_id + 1
    finally:
        connection.close()
        
def get_secret():

    secret_name = "chatstreamlit/mysql"
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    print(f'the secret is : {type(secret)},{secret}')


make_sidebar()

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

openai_api_key = get_secret()



st.title("💬 Communication")

current_user = st.session_state.get('user_info', {"user_id": None, "username": "unknown", "role": "dentist"})
user_id = current_user["user_id"]
user_role = current_user["role"]

if 'session_id' not in st.session_state or st.session_state['session_id'] is None:
    st.session_state['session_id'] = generate_session_id()

session_id = st.session_state['session_id']

if "messages" not in st.session_state or not st.session_state["messages"]:
    st.session_state["messages"] = [{"role": "patient", "content": "Hello, doctor. How are you today?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if dentist_input := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "dentist", "content": dentist_input})
    # show the message in the streamlit
    st.chat_message("dentist").write(dentist_input)
    # save the conversation
    insert_message(session_id, user_id, dentist_input, "dentist")
    
    
    context = "\n".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "dentist"])
    patient_response = generate_patient_conversation(dentist_input=dentist_input, context=context, openai_api_key=openai_api_key)

    st.session_state.messages.append({"role": "patient", "content": patient_response})
    # show the message in the streamlit
    st.chat_message("patient").write(patient_response)
    insert_message(session_id, user_id, patient_response, "patient")


