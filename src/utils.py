# src/utils.py

import streamlit.components.v1 as components
import streamlit as st

def get_screen_height():
    components.html("""
        <script>
            const height = window.innerHeight;
            const element = document.createElement("input");
            element.setAttribute("type", "hidden");
            element.setAttribute("id", "screen_height");
            element.setAttribute("value", height);
            document.body.appendChild(element);
        </script>
    """, height=0, width=0)

    # Use Streamlit's experimental function to retrieve the value from the hidden input
    screen_height = st.experimental_get_query_params().get("screen_height", [500])[0]
    return int(screen_height)
