import streamlit as st

from knowledge_base import KnowledgeBaseService

st.title("知识库更新服务")

uploader_file = st.file_uploader(
    label="请上传TXT文件",
    type=['txt'],
    accept_multiple_files=False,
)

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploader_file is not None:
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f} KB")

    if st.button("确认上传"):
        try:
            text = uploader_file.read().decode('utf-8')
            result = st.session_state["service"].upload_by_str(text, file_name)

            if result == "success":
                st.success("✅ 文件上传成功！")
            elif "[跳过]" in result:
                st.warning(f"⚠️ {result}")
            else:
                st.error(f"❌ 上传失败：{result}")
        except Exception as e:
            st.error(f"❌ 发生错误：{str(e)}")
