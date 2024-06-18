import streamlit as st
from PIL import Image
import io
from navigation import make_sidebar

make_sidebar()

def main():
    st.set_page_config(page_title="Profile", page_icon="👤")

    st.title("Profile")

    # Profile Header
    st.markdown("<style>.header {text-align: center;}</style>", unsafe_allow_html=True)

    if "avatar" not in st.session_state:
        st.session_state.avatar = "https://via.placeholder.com/100"

    st.markdown(
        f'<div class="header"><img src="{st.session_state.avatar}" alt="Avatar" style="border-radius:50%;width:100px;height:100px;"><h1>Peter</h1><a href="#">Edit Photo</a></div>',
        unsafe_allow_html=True
    )

    # Upload image for avatar
    uploaded_file = st.file_uploader("Choose a new profile picture", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Display the uploaded image
        st.image(image, caption='Uploaded Image.', use_column_width=True)

        # Update session state
        st.session_state.avatar = st.file_uploader
        st.success("Profile picture updated!")

    # Profile Options
    st.markdown('<div style="background-color:#fff;padding:20px;border-radius:10px;text-align:center;">',
                unsafe_allow_html=True)
    st.write("#### Feedback and Suggestion")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.write("#### Change Password")
    st.markdown('<hr>', unsafe_allow_html=True)

    # Suggestion Form
    st.markdown("### Feedback and Suggestion")
    suggestion = st.text_area("Write your suggestion here...")
    if st.button("Submit"):
        if suggestion.strip():
            st.success("Suggestion submitted successfully!")
        else:
            st.warning("Please write a suggestion before submitting.")


if __name__ == "__main__":
    main()
