import streamlit as st


def main():
    st.set_page_config(
        page_title="Profile",
        page_icon="👤"
    )
    
    st.sidebar.title("Profile")
    
    # Profile Header
    st.markdown("<style>.header {text-align: center;}</style>", unsafe_allow_html=True)
    st.markdown(
        '<div class="header"><img src="https://via.placeholder.com/100" alt="Avatar" style="border-radius:50%"><h1>Peter</h1><a href="#">Edit Photo</a></div>',
        unsafe_allow_html=True)
    
    # Profile Options
    st.markdown('<div style="background-color:#fff;padding:20px;border-radius:10px;text-align:center;">',
                unsafe_allow_html=True)
    st.write("#### Feedback and Suggestion")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.write("#### Change Password")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.write("#### Notifications")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Section
    st.markdown("<style>.performance {text-align: center; margin-top: 20px;}</style>", unsafe_allow_html=True)
    st.markdown(
        '<div class="performance"><div style="background-color:#6FAF92;width:100px;height:100px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:auto;"><h1 style="color:#fff;margin:0;">80</h1></div><h2>your performance</h2></div>',
        unsafe_allow_html=True)


if __name__ == "__main__":
    main()
