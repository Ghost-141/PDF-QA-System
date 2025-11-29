import asyncio
import os
import shutil
from typing import Optional

import torch
from fastapi import HTTPException
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from backend.services.interface.vector_store import VectorStoreInterface
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class VectorStoreManager(VectorStoreInterface):
    def __init__(self, persist_directory: Optional[str] = None):
        if persist_directory is None:
            base_dir = os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
            persist_directory = os.path.join(base_dir, "data", "vector_db")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(
            "Initializing VectorStoreManager with device '%s' and persist directory '%s'",
            device,
            persist_directory,
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": device},
        )
        self.persist_directory = persist_directory
        self.vector_store = None

    async def set_collection(self, collection_name: str) -> None:
        logger.info("Setting vector store collection to '%s'", collection_name)
        self.vector_store = await asyncio.to_thread(
            self._create_collection,
            collection_name,
        )

    def _create_collection(self, collection_name: str):
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
        )

    async def add_documents(self, documents) -> None:
        if not self.vector_store:
            logger.error("Attempted to add documents before initializing vector store.")
            raise HTTPException(status_code=500, detail="Vector store not initialized. Call set_collection first.")
        if not documents:
            logger.warning("No documents provided to add to vector store.")
            return
        await asyncio.to_thread(self.vector_store.add_documents, documents)
        logger.info("Added %d documents to the vector store.", len(documents))

    async def get_retriever(self, k_value: int = 6):
        if not self.vector_store:
            logger.error("Retriever requested before vector store initialization.")
            raise HTTPException(status_code=500, detail="Vector store not initialized. Call set_collection first.")
        logger.info("Creating retriever with top-k=%d", k_value)
        return await asyncio.to_thread(
            self.vector_store.as_retriever,
            search_kwargs={"k": k_value},
        )

    async def clean_database(self) -> None:
        if os.path.exists(self.persist_directory):
            logger.info("Cleaning vector store directory at %s", self.persist_directory)
            await asyncio.to_thread(shutil.rmtree, self.persist_directory)
            logger.info("Finished cleaning vector store directory.")
        else:
            logger.info("Vector store directory does not exist at %s; no cleanup needed.", self.persist_directory)
