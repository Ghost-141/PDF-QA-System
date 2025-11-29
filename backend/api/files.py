import asyncio
import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from backend.core.config import settings
from backend.core.dependency import (
    get_qa_pipeline_manager,
    get_upload_service,
    get_vector_store_manager,
)
from backend.models.api_models import ProcessFileResponse, UploadResponse
from backend.services.file_processor import FileProcessor
from backend.services.qa_service import QAPipelineManager
from backend.services.upload_service import UploadService
from backend.services.vector_store_service import VectorStoreManager
from backend.utils.logging_config import get_logger

router = APIRouter(tags=["files"])

logger = get_logger(__name__)


@router.post("/upload-file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service),
):
    logger.info("Received file upload for '%s'", file.filename)
    try:
        saved_path = await upload_service.save(file)
        filename = Path(saved_path).name
        logger.info("Upload complete. Stored at %s", saved_path)
        return UploadResponse(filename=filename)
    except Exception as exc:
        logger.exception("Failed to persist uploaded file '%s'", file.filename)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/process-file", response_model=ProcessFileResponse)
async def process_file(
    filename: str = Query(..., description="Filename to load from data/raw"),
    vector_store_manager: VectorStoreManager = Depends(get_vector_store_manager),
    qa_pipeline_manager: QAPipelineManager = Depends(get_qa_pipeline_manager),
):
    # Some clients may wrap the filename in quotes; normalize and drop any path segments.
    sanitized_filename = Path(filename.strip().strip('"').strip("'")).name
    file_path = settings.upload_dir / sanitized_filename
    logger.info("Received request to process file '%s' (sanitized to '%s')", filename, sanitized_filename)

    if not file_path.exists():
        logger.warning("File '%s' not found at %s", filename, file_path)
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in {settings.upload_dir}")

    try:
        await vector_store_manager.clean_database()
        logger.info("Cleaned vector store directory prior to processing.")

        collection_base = file_path.stem
        collection_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", collection_base).lower()
        collection_name = collection_name.strip("._-")
        if not collection_name:
            collection_name = "default_collection"
        if len(collection_name) < 3:
            collection_name = f"{collection_name}_kb"
        collection_name = collection_name[:63].strip("._-")
        if not collection_name:
            collection_name = "default_collection"
        if len(collection_name) < 3:
            collection_name = f"{collection_name}_kb"
        logger.info(
            "Resolved collection name '%s' for file '%s' (original base '%s')",
            collection_name,
            filename,
            collection_base,
        )

        file_processor = FileProcessor(str(file_path))
        docs = await asyncio.to_thread(file_processor.process)
        logger.info("File '%s' yielded %d document chunks", filename, len(docs) if docs else 0)

        if docs:
            await vector_store_manager.set_collection(collection_name)
            await vector_store_manager.add_documents(docs)
            retriever = await vector_store_manager.get_retriever()
            qa_pipeline_manager.create_pipeline(retriever)

            return ProcessFileResponse(
                message=(
                    f"File '{filename}' processed and added to the knowledge base with collection name "
                    f"'{collection_name}'."
                ),
                num_docs=len(docs),
            )

        logger.warning("No documents produced from file '%s'", filename)
        return ProcessFileResponse(message=f"File '{filename}' could not be processed or is empty.")
    except Exception as exc:
        logger.exception("Failed to process file '%s'", filename)
        raise HTTPException(status_code=500, detail=str(exc))
