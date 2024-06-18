import streamlit as st
from PIL import Image
import io
from navigation import make_sidebar
from service.mysql import get_connection

st.set_page_config(page_title="Profile", page_icon="👤")
make_sidebar()

def insert_suggestion(user, suggestion_content):
    value = (user, suggestion_content)
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO suggestions (user, suggestion_content) VALUES (%s, %s)"
            cursor.execute(sql, value)
            connection.commit()
    finally:
        connection.close()

def main():
    
    st.title("Profile")
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Please log in first.")
        return

    user_info = st.session_state.user_info
    user_with_quotes = user_info['username']
    user = user_with_quotes.replace('"', '')
    
    # Profile Header
    st.markdown("<style>.header {text-align: center;}</style>", unsafe_allow_html=True)

    if "avatar" not in st.session_state:
        st.session_state.avatar = "https://via.placeholder.com/100"

    st.markdown(
        f'<div class="header"><img src="{st.session_state.avatar}" alt="Avatar" style="border-radius:50%;width:100px;height:100px;"><h1>"{user}"</h1><a href="#">Edit Photo</a></div>',
        unsafe_allow_html=True
    )

    # Upload image for avatar
    uploaded_file = st.file_uploader("Choose a new profile picture", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')

        # Display the uploaded image
        st.image(image, caption='Uploaded Image.', use_column_width=True)

        # Update session state
        st.session_state.avatar = st.file_uploader
        st.success("Profile picture updated!")


    # Suggestion Form
    st.markdown("### Feedback and Suggestion")
    suggestion = st.text_area("Write your suggestion here...", key="suggestion_text")
    if "suggestions" not in st.session_state:
        st.session_state.suggestions = []
    if st.button("Submit"):
        if suggestion.strip():
            suggestion_content = suggestion.strip()
            # Insert into database
            insert_suggestion(user, suggestion_content)
            st.success("Suggestion submitted successfully!")
            # Clear the suggestion text
            # st.experimental_rerun()
        else:
            st.warning("Please write a suggestion before submitting.")


if __name__ == "__main__":
    main()
