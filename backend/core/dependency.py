from functools import lru_cache

from backend.core.config import settings
from backend.services.file_processor import FileProcessor
from backend.services.qa_service import QAPipelineManager
from backend.services.upload_service import UploadService
from backend.services.vector_store_service import VectorStoreManager
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


@lru_cache()
def get_vector_store_manager() -> VectorStoreManager:
    logger.debug("Providing VectorStoreManager singleton.")
    return VectorStoreManager(persist_directory=str(settings.vector_db_dir))


@lru_cache()
def get_qa_pipeline_manager() -> QAPipelineManager:
    logger.debug("Providing QAPipelineManager singleton.")
    return QAPipelineManager(api_key=settings.groq_api_key, model_name=settings.default_model)


@lru_cache()
def get_upload_service() -> UploadService:
    logger.debug("Providing UploadService singleton.")
    return UploadService(save_dir=settings.upload_dir)


def get_file_processor(file_path: str) -> FileProcessor:
    return FileProcessor(file_path)
