import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader

def load_uploaded_document(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not fount: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext == ".pdf":
        loader = PyPDFLoader(file_path)
    else:
        os.unlink(file_path)  # delete temp file
        raise ValueError(f"Unsupported file format: {ext}")

    documents = loader.load()

    # # Clean up temp file
    # os.unlink(file_path)

    return documents
