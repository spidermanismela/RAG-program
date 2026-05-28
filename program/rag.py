from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, format_document, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
import config_data as config
from program.file_history_store import get_history
from program.vector_stores import VectorStoreService


class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model="text-embedding-v4",
                                          dashscope_api_key=config.key))
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的参考资料为主：简洁和专业的回答用户的问题，参考资料：{context}。"),
                ("system", "并且历史对话记录如下:"),
                MessagesPlaceholder("history"),
                ("human", "{question}"),
            ],
        )
        self.chat_model = ChatTongyi(model="qwen3.7-max", dashscope_api_key=config.key)
        self.chain = self.__get_chain()

    def __get_chain(self):
        retriever = self.vector_service.get_retriever()

        def format_document(docs: list[Document]):
            if not docs:
                return "无相关检索材料"

            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str

        def daying(prompt):
            print(prompt.to_string())
            return prompt

        def format_for_retriever(value:dict)->str:
            return value["question"]

        def format_for_prompt(value):
            new_value={}
            new_value["question"]=value["question"]["question"]
            new_value["history"]=value["question"]["history"]
            new_value["context"]=value["context"]
            return new_value

        chain = (
                {
                    "question": RunnablePassthrough(),
                    "context": RunnableLambda(format_for_retriever)|retriever | format_document
                } |RunnableLambda(format_for_prompt) | self.prompt_template | daying | self.chat_model | StrOutputParser()
        )
        converted_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        return converted_chain


if __name__ == '__main__':
    session_config = {
        "configurable": {
            "session_id": "test",
        }
    }
    service = RagService()
    print(service.chain.invoke({"question": "我身高185，尺码推荐  "}, session_config))
