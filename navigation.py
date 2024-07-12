import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]

def make_sidebar():
    with st.sidebar:
        st.title("🦷 Welcome to dentist")
        

        if st.session_state.get("logged_in", False):
            st.page_link("pages/1Profile.py", label="Profile") # , icon="👤‍‍"
            st.page_link("pages/2Communication.py", label="Communication") # , icon="💬"
            st.page_link("pages/3History Conversation.py", label="History Conversation") # , icon="📝"
            st.page_link("pages/4History Detail Conversation.py", label="History Detail Conversation")
            st.page_link("pages/5Admin.py", label="Admin Setting")

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "login":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("login.py")


def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")

    st.switch_page("login.py")