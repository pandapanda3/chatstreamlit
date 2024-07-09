# src/utils.py

import streamlit.components.v1 as components
import streamlit as st

def setup_screen_height_listener():
    st.experimental_js('''
        window.addEventListener('message', (event) => {
            if (event.data.type && event.data.type === 'height') {
                window.location.search = '?screen_height=' + event.data.value;
            }
        });
    ''')

# 定义一个新的 Streamlit 组件，用于获取屏幕高度
def get_screen_height():
    setup_screen_height_listener()  # 确保监听器已设置

    components.html("""
        <script>
            const height = window.innerHeight;
            const message = {type: 'height', value: height};
            window.parent.postMessage(message, '*');
        </script>
    """, height=0, width=0)

    # 使用 Streamlit 的特殊事件机制接收消息
    screen_height = st.experimental_get_query_params().get("screen_height", [500])[0]
    return int(screen_height)
