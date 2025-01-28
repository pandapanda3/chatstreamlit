import streamlit as st
from navigation import make_sidebar
from service.information_from_mysql import authenticate_user, create_user, update_password, existing_user
import os
if st.session_state.get('logged_in', False):
    make_sidebar()

st.title("Welcome to The Platform")

if not st.session_state.get('logged_in', False):
    st.write("Please log in to continue.")

    Login, Register, Reset = st.tabs(["Login", "Register", "Reset Password"])

    # Login
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

    # Register
    with Register:
        new_username = st.text_input("Username", key="Register_username")
        student_number = st.text_input("Student Number", key='Register_student_number')
        new_password = st.text_input("New Password", type="password", key="Register_new_password")
        new_password_confirm = st.text_input("Confirm New Password", type="password", key="Register_new_password_confirm")
        if st.button("Register"):
            existing = existing_user(new_username, student_number)
            print(f'Register - existing value :{existing}')
            if existing:
                st.error("The Account already exist!")
            else:
                if new_password == new_password_confirm:
                    create_user(new_username, new_password, student_number)
                    st.success("Account created successfully!")
                else:
                    st.error("Passwords do not match. Please try again.")

    # Reset
    with Reset:
        reset_username = st.text_input("Username", key="Reset_username")
        student_number = st.text_input("Student Number", key='Reset_student_number')
        new_password = st.text_input("New Password", type="password", key="Reset_new_password")
        new_password_confirm = st.text_input("Confirm New Password", type="password", key="Reset_new_password_confirm")
        if st.button("Update Password"):
            existing = existing_user(reset_username, student_number)
            if existing:
                if new_password == new_password_confirm:
                    update_password(reset_username, new_password, student_number)
                    st.success("Password updated successfully!")
                else:
                    st.error("Passwords do not match. Please try again.")
            else:
                st.error("Make sure you input the correct Username and Student Number, or ensure that you have registered.")
else:
    st.write("You are already logged in.")

st.markdown("""
# Hi everyone,

I’m a recent graduate from the **Department of Informatics**. It’s a pleasure to see you all using this platform. I hope everyone can actively share their valuable suggestions.

---

### **Important Notes:**

1. Using this platform on a computer offers a more user-friendly experience. When accessing the platform on a mobile device, navigate to the Communication Page and click the button in the top-left corner to open the sidebar, where you can view patient details and other information.

2. If you encounter instances where the chatbot simulates a dentist’s tone during conversations, or if you discover other bugs:
   - Please try logging out and then logging back in to see if the issue persists.
   - If the problem continues, you can provide feedback via the suggestion box on your **profile page**.
     Make sure to include:
     - Details about the actions you took.
     - The errors you encountered.

3. Before you leave, we kindly ask you to:
   - Scan the QR code of the questionnaire.
   - Provide your feedback through the **AI-based portal evaluation questionnaire**.

---

Thank you for your cooperation!
""")

current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"second working directory: {current_dir}")
platform_image_path = os.path.join(current_dir, "platform_qr_code.png")
questionnaire_image_path = os.path.join(current_dir, "questionnaire_qr_code.png")

print(f"Current image_path : {platform_image_path}")
st.image(platform_image_path, caption="QR Code for Platform", width=100)
# st.image('/chatstreamlit/platform_qr_code.png', caption="QR Code for Platform", width=60)
st.image('platform_image_path', caption="QR Code for Questionnaire", width=100)