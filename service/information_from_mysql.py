from service.mysql import get_connection


# get all the chat history of certain session_id
def get_session_chat_detail(session_id):
    value = (session_id,)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT user_role, message FROM chat_records WHERE session_id = %s"
            cursor.execute(sql, value)
            result = cursor.fetchall()
            
            return result
    
    finally:
        connection.close()


# get patient symptoms of certain session_id
def get_patient_symptoms_detail(session_id):
    value = (session_id,)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT patient_details FROM user_chat_history WHERE session_id = %s"
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
    
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO user_chat_history (user_id, user_name, chat_count, patient_details, session_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, value)
            connection.commit()
    
    finally:
        connection.close()


# update the quality of user_chat_history
def update_user_chat_history_quality(user_id, user_name, chat_count, conversation_score):
    value = (conversation_score, user_id, user_name, chat_count)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE user_chat_history SET conversation_score = %s WHERE user_id = %s AND user_name = %s AND chat_count = %s"
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
            if result and len(result) > 0:
                max_session_id = result[0] if result[0] is not None else 0
            else:
                max_session_id = 0
            return max_session_id + 1
    finally:
        connection.close()