from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import asyncio
import os
import shutil
import torch
from fastapi import HTTPException
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    def __init__(self, persist_directory=None):
        if persist_directory is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_directory = os.path.join(base_dir, "chroma_langchain_db")

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(
            "Initializing VectorStoreManager with device '%s' and persist directory '%s'",
            device,
            persist_directory,
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="Alibaba-NLP/gte-modernbert-base",
            model_kwargs={'device': device}
        )
        self.persist_directory = persist_directory
        self.vector_store = None

    async def set_collection(self, collection_name):
        logger.info("Setting vector store collection to '%s'", collection_name)
        self.vector_store = await asyncio.to_thread(
            self._create_collection,
            collection_name,
        )

    def _create_collection(self, collection_name):
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
        )

    async def add_documents(self, documents):
        if not self.vector_store:
            logger.error("Attempted to add documents before initializing vector store.")
            raise HTTPException(status_code=500, detail="Vector store not initialized. Call set_collection first.")
        if not documents:
            logger.warning("No documents provided to add to vector store.")
            return
        await asyncio.to_thread(self.vector_store.add_documents, documents)
        logger.info("Added %d documents to the vector store.", len(documents))

    async def get_retriever(self, k_value=6):
        if not self.vector_store:
            logger.error("Retriever requested before vector store initialization.")
            raise HTTPException(status_code=500, detail="Vector store not initialized. Call set_collection first.")
        logger.info("Creating retriever with top-k=%d", k_value)
        return await asyncio.to_thread(
            self.vector_store.as_retriever,
            search_kwargs={"k": k_value},
        )

    async def clean_database(self):
        if os.path.exists(self.persist_directory):
            logger.info("Cleaning vector store directory at %s", self.persist_directory)
            await asyncio.to_thread(shutil.rmtree, self.persist_directory)
            logger.info("Finished cleaning vector store directory.")
        else:
            logger.info("Vector store directory does not exist at %s; no cleanup needed.", self.persist_directory)


async def save_uploaded_file(uploaded_file, save_dir="./data/raw"):
    """
    Save a FastAPI UploadFile to the specified directory.

    Args:
        uploaded_file: FastAPI UploadFile object
        save_dir: directory path where to save the file

    Returns:
        str: absolute path of the saved file
    """
    logger.info("Saving uploaded file '%s' to directory '%s'", uploaded_file.filename, save_dir)
    await asyncio.to_thread(os.makedirs, save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, uploaded_file.filename)

    def _persist_file():
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)

    try:
        await asyncio.to_thread(_persist_file)
    except Exception:
        logger.exception("Failed to persist uploaded file '%s'", uploaded_file.filename)
        raise

    abs_path = os.path.abspath(file_path)
    logger.info("Saved file to %s", abs_path)
    return abs_path
