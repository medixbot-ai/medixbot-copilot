from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings


# Extract data from the PDF
def pdf_loader(data):
    """Load PDF files from a folder and parse them into a list of text documents.

    Args:
        data (str): The path to the folder containing PDF files.

    Returns:
        list: A list of text documents extracted from the PDF files.
    """
    loader = DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents


# Create text chunks
def text_spliter(extracted_data):
    """Split the list of text into chunks.

    Args:
        extracted_data (list): List of text to be split.

    Returns:
        list: List of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks


# download embedding model
def download_hugging_face_embeddings(model_name):
    """Download a Hugging Face model for embeddings.

    Args:
        model_name (str): The name of the Hugging Face model to download.

    Returns:
        embeddings: An instance of the downloaded model for embeddings.
    """
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings
