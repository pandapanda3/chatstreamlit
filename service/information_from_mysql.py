from service.mysql import get_connection
import bcrypt
from service.locker_manager import session_id_lock, insert_chat_history_lock
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

# check if the user exist
def existing_user(username, student_number):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, password, role FROM users WHERE username = %s and student_number = %s"
            cursor.execute(sql, (username, student_number))
            result = cursor.fetchone()
            print(f'the existing_user is {username},{student_number}')
            if result:
                return True
            else:
                return False
    finally:
        connection.close()
        
def create_user(username, password, student_number, role='normal'):
    connection = get_connection()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password, student_number, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, student_number, role))
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
        
# get all the chat history of certain session_id
def get_session_chat_detail(session_id):
    value = (session_id,)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT user_role, message, quality FROM chat_records WHERE session_id = %s"
            cursor.execute(sql, value)
            result = cursor.fetchall()
            
            return result
    
    finally:
        connection.close()


# insert into performance in the user_chat_history
def insert_performance_feedback(performance_feedback,session_id):
    value = (performance_feedback,session_id)
    connection = get_connection()
    print(f'Update user_chat_history information in performance_feedback: {session_id}: {performance_feedback}')
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE user_chat_history SET performance_feedback = %s WHERE session_id = %s"
            cursor.execute(sql, value)
            connection.commit()
            if cursor.rowcount > 0:
                return True
    finally:
        connection.close()

# get patient details of certain session_id
def get_patient_symptoms_detail(session_id):
    value = (session_id,)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT patient_details, conversation_score, performance_feedback,scenario, emotion, publish_conversation FROM user_chat_history WHERE session_id = %s"
            cursor.execute(sql, value)
            result = cursor.fetchall()
            
            return result
    
    finally:
        connection.close()


# insert chat_records of message and user_role
def insert_message(session_id, user_id, message, user_role, message_id):
    value = (session_id, user_id, message, user_role, message_id)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO chat_records (session_id, user_id, message, user_role, message_id) VALUES (%s, %s, %s, %s, %s)"
            print(f'Insert chat_records: {sql}, VALUE IS : {value}')
            cursor.execute(sql, value)
            connection.commit()
    
    finally:
        connection.close()


# update the quality of each message in chat_records
def update_quality_of_each_message(session_id, user_id, message_id, quality):
    value = (quality, session_id, user_id, message_id)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE chat_records SET quality = %s WHERE session_id = %s AND user_id = %s AND message_id = %s"
            cursor.execute(sql, value)
            connection.commit()
    
    finally:
        connection.close()
        
# get the largest number of chat_count of the user
def get_largest_chat_number(user_id):
    value = (user_id)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT MAX(chat_count) AS max_chat_count FROM user_chat_history WHERE user_id = %s"
            cursor.execute(sql, value)
            result = cursor.fetchone()
            if result and len(result) > 0:
                max_chat_count = result[0] if result[0] is not None else 0
            else:
                max_chat_count = 0
            return max_chat_count
    
    finally:
        connection.close()


# insert user_chat_history
def insert_user_chat_history(user_id, user_name, chat_count, patient_details, session_id):
    value = (user_id, user_name, chat_count, patient_details, session_id)
    connection = get_connection()
    with insert_chat_history_lock:
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO user_chat_history (user_id, user_name, chat_count, patient_details, session_id) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, value)
                connection.commit()
        
        finally:
            connection.close()


# update the information of the conversation of a session
def update_user_chat_history(user_id, user_name, chat_count, certain_column_name, certain_column_value):
    value = (certain_column_value, user_id, user_name, chat_count)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = f"UPDATE user_chat_history SET {certain_column_name} = %s WHERE user_id = %s AND user_name = %s AND chat_count = %s"
            result = cursor.execute(sql, value)
            print(f'update information: {sql}')
            connection.commit()
    except Exception as e:
        print(f'An error occurred: {e}')
        connection.rollback()
    finally:
        connection.close()

# generate session id
def generate_session_id():
    with session_id_lock:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT MAX(session_id) FROM chat_records")
                result = cursor.fetchone()
                print(f'')
                if result and len(result) > 0:
                    max_session_id = result[0] if result[0] is not None else 0
                else:
                    max_session_id = 0
                print(f'generate session id is {max_session_id + 1}')
                return max_session_id + 1
        finally:
            connection.close()
        
#  Fetch data from user_chat_history
def fetch_chat_history_data(user_id,role):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if role == 'admin':
                # for the admin user , they can check the data of publish_conversation = 1 (agree to get feedback from lecturer) and the conversation generated by himself.
                sql = "SELECT session_id, chat_count, user_name, scenario, emotion, patient_details, conversation_score, performance_feedback, publish_conversation FROM user_chat_history where publish_conversation =  1 or user_id =  %s"
            else:
                sql = "SELECT session_id, chat_count, user_name, scenario, emotion, patient_details, conversation_score, performance_feedback, publish_conversation FROM user_chat_history where user_id =  %s"

            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


# get all users' name, student_number, role
def get_users_role():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT username, student_number, role FROM users order by role"
            cursor.execute(sql, )
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
        
# get all users' name, student_number, role
def update_users_role(user_name, k_number,role):
    value = (role, user_name, k_number)
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET role = %s WHERE username = %s AND student_number = %s"
            cursor.execute(sql, value)
            connection.commit()
            if cursor.rowcount > 0:
                return True
    except Exception as e:
        print(f'An error occurred: {e}')
        connection.rollback()
    finally:
        connection.close()
        
# get scenarios
def get_scenarios():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT scenario_name FROM scenario"
            cursor.execute(sql, )
            result = cursor.fetchall()
            return result
    finally:
        connection.close()

# get emotion
def get_emotions():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT emotion_name FROM emotion"
            cursor.execute(sql, )
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
        
# get quality
def get_quality():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT quality FROM chat_records where quality != ''"
            cursor.execute(sql, )
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
        
# get CONVERSATION SCORE
def get_conversation_score():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT conversation_score FROM user_chat_history where conversation_score != ''"
            cursor.execute(sql, )
            result = cursor.fetchall()
            return result
    finally:
        connection.close()