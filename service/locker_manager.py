import threading

# generate the lock of session_id
session_id_lock = threading.Lock()

# generate the lock of user_chat_history
insert_chat_history_lock = threading.Lock()
