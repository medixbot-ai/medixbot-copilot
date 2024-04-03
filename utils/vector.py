from utils.docs import pdf_loader, text_spliter, download_hugging_face_embeddings
from utils.exceptions import CustomExption
from utils.logger import logger
import pinecone
from langchain.vectorstores import Pinecone
from dotenv import load_dotenv
from utils.prompt import prompt_template
import os


def config(index_name=None, api_key=None, env=None, read_dot_env=True):

    config = dict()

    if read_dot_env:
        load_dotenv()

        config["index_name"] = os.environ.get("INDEX_NAME")
        config["api_key"] = os.environ.get("PINECONE_API_KEY")
        config["env"] = os.environ.get("PINECONE_API_ENV")
        config["huggingface_model"] = os.environ.get("HUGGING_FACE_MODEL")
    else:
        config["index_name"] = index_name
        config["api_key"] = api_key
        config["env"] = env

    return config


class Vector:

    def __init__(self, pinecone_cred, embedding_model, dimension) -> None:
        if not isinstance(pinecone_cred, dict):
            raise CustomExption("Pinecone credentials must dictionarie type")
            return

        self.api_key = pinecone_cred["api_key"]
        self.index_name = pinecone_cred["index_name"]
        self.env = pinecone_cred["env"]
        self.embeddings = embedding_model
        self.dimension = dimension

    @property
    def index(self):
        return self.index_name

    def connect(self):
        try:
            pinecone.init(api_key=self.api_key, environment=self.env)

        except CustomExption as e:
            logger.exception("Error occured when connecting to the pinecone: ", e)

    def _reset(self, index_name=None):
        index_name = index_name if index_name else self.index_name
        try:
            pinecone.delete_index(index_name)
        except CustomExption as e:
            logger.exception(
                f"Error occured when try to delete index {index_name}: ", e
            )

    def _create(self, index_name=None):
        index_name = index_name if index_name else self.index_name

        try:
            pinecone.create_index(index_name, dimension=self.dimension)
            logger.info("Vector created successfully")

        except CustomExption as e:
            logger.exception(
                f"Error occured when trying to create index {index_name}: ", e
            )

    def populate(self, folder, index_name=None):
        index_name = index_name if index_name else self.index_name

        print("index_list: ", pinecone.list_indexes())
        if index_name not in pinecone.list_indexes():
            self._create(index_name=index_name)
        else:
            self._reset(index_name=index_name)
            self._create(index_name=index_name)

        raw_text = pdf_loader(folder)
        chunk_text = text_spliter(raw_text)

        try:
            Pinecone.from_texts(
                [
                    t.page_content + " {source:" + '"' + t.metadata["source"] + '"}'
                    for t in chunk_text
                ],
                self.embeddings,
                index_name=self.index_name,
            )

        except CustomExption as e:
            logger.exception("Error occured when creating ")

    def retrieve(self, index_name=None):

        if index_name:
            return Pinecone.from_existing_index(index_name, self.embeddings)
        else:
            return Pinecone.from_existing_index(self.index_name, self.embeddings)
