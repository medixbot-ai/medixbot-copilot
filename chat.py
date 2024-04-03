from utils.vector import config, Vector
from utils.exceptions import CustomExption
from utils.logger import logger
from langchain_openai import OpenAIEmbeddings
from utils.llama_wrapper import llama_api_calling, openai_api_calling
from utils.docs import download_hugging_face_embeddings
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os


if __name__ == "__main__":

    load_dotenv()
    use_openai = os.environ.get("USE_OPENAI")
    pinecone_creds = config()

    if use_openai == "True":
        embedding_model = OpenAIEmbeddings()
        vector_instance = Vector(
            pinecone_creds, embedding_model=embedding_model, dimension=1536
        )
        vector_instance.connect()
    else:
        embedding_model = download_hugging_face_embeddings(
            os.environ.get("HUGGING_FACE_MODEL")
        )
        vector_instance = Vector(
            pinecone_creds, embedding_model=embedding_model, dimension=348
        )

        # connect to pinecone database
        vector_instance.connect()
        # llama
        conversation_agent = llama_api_calling(vector_instance=vector_instance)

    st.title("Medixbot Copilot")
    if "user_input" not in st.session_state:
        st.session_state["user_input"] = []

    if "medixbot" not in st.session_state:
        st.session_state["medixbot"] = []

    def get_text():
        input_text = st.text_input("Write your questions here", key="input")
        return input_text

    user_input = get_text()

    if user_input:
        if use_openai == "False":
            output = conversation_agent.question_answer(user_input)
            result = output["result"]
            # source = output["source"]
            output = result.lstrip("\n")  # +"\nsource: "+source.lstrip("\n")

        else:
            output = openai_api_calling(os.environ.get("INDEX_NAME"), user_input)

        # Store the output
        st.session_state.medixbot.append(user_input)
        st.session_state.user_input.append(output)

    message_history = st.empty()

    if st.session_state["user_input"]:
        for i in range(len(st.session_state["user_input"]) - 1, -1, -1):
            # This function displays user input
            message(
                st.session_state["user_input"][i],
                key=str(i),
                avatar_style="adventurer",
            )
            # This function displays medixbot response
            message(
                st.session_state["medixbot"][i],
                avatar_style="miniavs",
                is_user=True,
                key=str(i) + "data_by_user",
            )
