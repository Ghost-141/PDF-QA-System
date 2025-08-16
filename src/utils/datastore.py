from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import shutil
import torch
from fastapi import HTTPException

class VectorStoreManager:
    def __init__(self, persist_directory=None):
        if persist_directory is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_directory = os.path.join(base_dir, "chroma_langchain_db")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="Alibaba-NLP/gte-modernbert-base",
            model_kwargs={'device': device}
        )
        self.persist_directory = persist_directory
        self.vector_store = None

    def set_collection(self, collection_name):
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
        )

    def add_documents(self, documents):
        if not self.vector_store:
            raise HTTPException(status_code=500, detail="Vector store not initialized. Call set_collection first.")
        if not documents:
            return
        self.vector_store.add_documents(documents)
        print(f"[DEBUG] Added {len(documents)} documents to the vector store.")

    def get_retriever(self, k_value=6):
        if not self.vector_store:
            raise HTTPException(status_code=500, detail="Vector store not initialized. Call set_collection first.")
        return self.vector_store.as_retriever(search_kwargs={"k": k_value})

    def clean_database(self):
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            print(f"[DEBUG] Cleaned database at {self.persist_directory}")


def save_uploaded_file(uploaded_file, save_dir="./data/raw"):
    """
    Save a FastAPI UploadFile to the specified directory.

    Args:
        uploaded_file: FastAPI UploadFile object
        save_dir: directory path where to save the file

    Returns:
        str: absolute path of the saved file
    """
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, uploaded_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    
    abs_path = os.path.abspath(file_path)
    print(f"[DEBUG] Saved file to: {abs_path}")
    print(f"[DEBUG] Directory contents: {os.listdir(save_dir)}")
    
    return abs_path