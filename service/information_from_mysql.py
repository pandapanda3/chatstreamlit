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