from utils.langchain_wrapper import ConfigLangChain
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.vectorstores import Pinecone
from utils.prompt import prompt_template
import os


load_dotenv()
use_openai = os.environ.get("USE_OPENAI")
model_name = os.environ.get("OPENAI_MODEL")
max_tokens = int(os.environ.get("OPENAI_MAX_TOKENS"))
temperature = float(os.environ.get("TEMPERATURE"))
llama_model = os.environ.get("LLAMA_MODEL_DIR")
open_ai_key = os.environ.get("OPENAI_API_KEY")
embedding_model_name = os.environ.get("EMBEDDING_MODEL_NAME")

client = ""
if use_openai == "True":
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")


def openai_api_calling(index_name, query):

    embedded_model = OpenAIEmbeddings(model=embedding_model_name)
    llm = ChatOpenAI(model=model_name)
    prompt = ChatPromptTemplate.from_template(prompt_template)

    index_search = Pinecone.from_existing_index(index_name, embedded_model)

    docs = index_search.similarity_search(query)

    context = "\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": lambda x: context, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    result = chain.invoke(query)
    return result


def llama_api_calling(vector_instance):

    chains = ConfigLangChain(
        model_folder=llama_model,
        max_token=max_tokens,
        temperature=temperature,
        vector_instance=vector_instance,
    )

    return chains
