from service.mysql import get_connection


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
    
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE user_chat_history SET performance_feedback = %s WHERE session_id = %s"
            cursor.execute(sql, value)
            connection.commit()
    
    finally:
        connection.close()

# get patient symptoms of certain session_id
def get_patient_symptoms_detail(session_id):
    value = (session_id,)
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT patient_details, conversation_score, performance_feedback FROM user_chat_history WHERE session_id = %s"
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
    
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO user_chat_history (user_id, user_name, chat_count, patient_details, session_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, value)
            connection.commit()
    
    finally:
        connection.close()


# update the quality of the conversation of a session
def update_user_chat_history_quality(user_id, user_name, chat_count, conversation_score):
    value = (conversation_score, user_id, user_name, chat_count)
    connection = get_connection()
    print(f'UPDATE the quality of user_chat_history: conversation_score {conversation_score}: {type(conversation_score)}, user_id {user_id} : {type(user_id)}, user_name {user_name} : {type(user_name)}, chat_count {chat_count}:{type(chat_count)}\n')
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE user_chat_history SET conversation_score = %s WHERE user_id = %s AND user_name = %s AND chat_count = %s"
            result = cursor.execute(sql, value)
            print(f'the result is {result}')
            connection.commit()
    except Exception as e:
        print(f'An error occurred: {e}')
        connection.rollback()
    finally:
        connection.close()

# generate session id
def generate_session_id():
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