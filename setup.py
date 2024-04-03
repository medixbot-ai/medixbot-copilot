from utils.vector import Vector, config
from utils.logger import logger
from utils.exceptions import CustomExption
import requests
import os
from langchain_openai import OpenAIEmbeddings
from glob import glob
from dotenv import load_dotenv
from utils.docs import download_hugging_face_embeddings


def check_file(directory, extention):
    # Search for all files with .bin extension in the given directory
    bin_files = glob(f"{directory}/{extention}")

    if bin_files:
        return True
    else:
        return False


# TODO: This function is not working as espected. Download the model manually instead
def download_model(model_link):

    if not check_file("model", "*.bin"):
        # Send a GET request to download the model
        try:

            print(f"Downloading model {model_link} ...")
            response = requests.get(model_link)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:

                # Save the downloaded model to a file
                load_dotenv()
                with open(os.environ.get("LLAMA_MODEL_DIR"), "wb") as f:
                    f.write(response.content)
                    print("Model downloaded successfully.")
            else:
                print("Failed to download the model.")
        except CustomExption as e:
            logger.exception(f"Error occured when downloding the model {model_link}")
    else:
        print(
            "Skip. Model already downloded. If you want to work with another model, please delete the existing one first"
        )


def populate_vector(data_path, embedding_model, dimension):

    if not check_file(data_path, "*.pdf"):
        print(f"Right now {data_path} is empty. Please put your pdf documents here")
        return

    env_config = config()
    vector_instance = Vector(
        env_config, embedding_model=embedding_model, dimension=dimension
    )
    print(
        f"Please wait, we are populating your vector database which have indexname {vector_instance.index}"
    )
    vector_instance.connect()
    vector_instance.populate(data_path)
    print(f"{vector_instance.index} populated succesfully")


if __name__ == "__main__":
    load_dotenv()

    model_link = os.environ.get("LLAMA_MODEL_URL")
    data_path = os.environ.get("DATA_PATH")
    llama_model_name = os.environ.get("HUGGING_FACE_MODEL")
    config_for_openai = os.environ.get("USE_OPENAI")

    if config_for_openai == "True":
        embedding_model = OpenAIEmbeddings()
        populate_vector(
            data_path=data_path, embedding_model=embedding_model, dimension=1536
        )
    else:

        embedding_model = download_hugging_face_embeddings(llama_model_name)
        download_model(model_link=model_link)
        populate_vector(
            data_path=data_path, embedding_model=embedding_model, dimension=384
        )

    print("Finish setup successfully ✨ 🍰 ✨")
