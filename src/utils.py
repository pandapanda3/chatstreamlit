# src/utils.py

import streamlit.components.v1 as components

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

    screen_height = st_js('document.getElementById("screen_height").value')
    return int(screen_height) if screen_height else 500

def st_js(js):
    result = components.html(f"""
        <script>
            const result = {js};
            const element = document.createElement("input");
            element.setAttribute("type", "hidden");
            element.setAttribute("id", "result");
            element.setAttribute("value", result);
            document.body.appendChild(element);
        </script>
    """, height=0, width=0)
    return result
