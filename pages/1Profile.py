import streamlit as st
from PIL import Image, UnidentifiedImageError
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

# save the image of avatar
def update_avatar(user_id, avatar_data):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET profile_image = %s WHERE id = %s"
            cursor.execute(sql, (avatar_data, user_id))
            connection.commit()
    finally:
        connection.close()
        
def get_avatar(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT profile_image FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    finally:
        connection.close()

def main():
    
    st.title("Profile")
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Please log in first.")
        return

    user_info = st.session_state.user_info
    user = user_info['username']
    user_id = user_info['user_id']
    print(f'information of session_state: {st.session_state}')
    
    # Load the user's avatar from the database
    avatar_data = get_avatar(user_id)
    if avatar_data:
        try:
            avatar_image = Image.open(io.BytesIO(avatar_data))
            st.session_state.avatar = avatar_image
        except UnidentifiedImageError:
            st.session_state.avatar = "https://via.placeholder.com/100"
            st.error("Failed to load avatar image.")
    else:
        st.session_state.avatar = "https://via.placeholder.com/100"

    # Profile Header
    st.markdown("<style>.header {text-align: center;}</style>", unsafe_allow_html=True)

    # Display the avatar
    if avatar_data:
        st.image(st.session_state.avatar, width=100, caption=user)
    else:
        st.markdown(
            f'<div class="header"><img src="{st.session_state.avatar}" alt="Avatar" style="border-radius:50%;width:100px;height:100px;"><h1>"{user}"</h1></div>',
            unsafe_allow_html=True
        )
    

    # Upload image for avatar
    uploaded_file = st.file_uploader("Choose a new profile picture", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        # Update the avatar in the database
        update_avatar(user_id, img_byte_arr)

        # Reload the avatar from the database to display
        avatar_data = get_avatar(user_id)
        try:
            avatar_image = Image.open(io.BytesIO(avatar_data))
            st.session_state.avatar = avatar_image
        except UnidentifiedImageError:
            st.session_state.avatar = "https://via.placeholder.com/100"
            st.error("Failed to load updated avatar image.")
        st.success("Profile picture updated!")
        
    st.markdown(
        f'<div class="header"><img src="{st.session_state.avatar}" alt="Avatar" style="border-radius:50%;width:100px;height:100px;"><h1>"{user}"</h1></div>',
        unsafe_allow_html=True
    )
    
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
