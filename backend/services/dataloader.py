import os
from typing import Any, Sequence

from langchain_community.document_loaders import PyPDFLoader, TextLoader

from backend.services.interface.dataloader import DataLoaderInterface
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class DataLoader(DataLoaderInterface):
    def load(self, file_path: str) -> Sequence[Any]:
        logger.info("Loading uploaded document from %s", file_path)

        if not os.path.exists(file_path):
            logger.error("Uploaded file missing: %s", file_path)
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        logger.info("Detected extension '%s' for %s", ext, file_path)

        try:
            if ext == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
                logger.info("Using TextLoader for %s", file_path)
            elif ext == ".pdf":
                loader = PyPDFLoader(file_path)
                logger.info("Using PyPDFLoader for %s", file_path)
            else:
                logger.error("Unsupported file format '%s' for %s", ext, file_path)
                os.unlink(file_path)
                raise ValueError(f"Unsupported file format: {ext}")

            documents = loader.load()
            logger.info("Loaded %d documents from %s", len(documents), file_path)
            return documents
        except Exception:
            logger.exception("Failed to load uploaded document from %s", file_path)
            raise
