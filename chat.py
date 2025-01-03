from dotenv import load_dotenv
from llm import get_response
import streamlit as st
import os 

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="SJSU CS Assistant", page_icon="🤖")

st.title("🤖 SJSU CS Assistant")
st.caption("Ask anything about SJSU Computer Science instructors!")


if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])




if user_question := st.chat_input(placeholder="Ask your questions about SJSU Computer Science instructors!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.spinner("Generating response..."):
        response = get_response(user_question)
        with st.chat_message("ai"):
            message = st.write_stream(response)
            st.session_state.message_list.append({"role": "ai", "content": message})