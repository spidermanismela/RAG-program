import streamlit as st
from rag import RagService

st.title("智能客服")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，有什么可以帮助你？"}]

if "service" not in st.session_state:
    st.session_state["service"] = RagService()
    st.session_state["session_config"] = {
        "configurable": {"session_id": "default_user"}
    }

for msg in st.session_state["message"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("请输入您的问题...")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("AI思考中..."):
            try:
                response = st.session_state["service"].chain.invoke(
                    {"question": prompt},
                    st.session_state["session_config"]
                )
                st.write(response)
                st.session_state["message"].append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ 发生错误：{str(e)}"
                st.write(error_msg)
                st.session_state["message"].append({"role": "assistant", "content": error_msg})
