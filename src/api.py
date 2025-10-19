from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import re
from pydantic import BaseModel
from src.utils.file_processor import FileProcessor
from src.utils.datastore import VectorStoreManager, save_uploaded_file
from src.utils.retriever import QAPipelineManager
from src.utils.logging_config import get_logger

# Folder for uploads
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Q/A based RAG API",
    description="API for question-answering using RAG pipeline",
    version="1.0.0"
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store_manager = VectorStoreManager()
qa_pipeline_manager = QAPipelineManager()
logger = get_logger(__name__)

class Question(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "Bangla RAG API is up!"}

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    logger.info("Received file upload for '%s'", file.filename)
    try:
        saved_path = await save_uploaded_file(file, save_dir=UPLOAD_DIR)
        filename = os.path.basename(saved_path)
        logger.info("Upload complete. Stored at %s", saved_path)
        return {"filename": filename}
    except Exception as exc:
        logger.exception("Failed to persist uploaded file '%s'", file.filename)
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/process-file")
async def process_file(filename: str = Query(..., description="Filename to load from data/raw")):
    file_path = os.path.join(UPLOAD_DIR, filename)
    logger.info("Received request to process file '%s'", filename)

    if not os.path.exists(file_path):
        logger.warning("File '%s' not found at %s", filename, file_path)
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in {UPLOAD_DIR}")

    try:
        await vector_store_manager.clean_database()
        logger.info("Cleaned vector store directory prior to processing.")

        collection_base = os.path.splitext(filename)[0]
        collection_name = re.sub(r'[^a-zA-Z0-9._-]+', '_', collection_base).lower()
        collection_name = collection_name.strip('._-')
        if not collection_name:
            collection_name = "default_collection"
        if len(collection_name) < 3:
            collection_name = f"{collection_name}_kb"
        collection_name = collection_name[:63].strip('._-')
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

        file_processor = FileProcessor(file_path)
        docs = await asyncio.to_thread(file_processor.process)
        logger.info("File '%s' yielded %d document chunks", filename, len(docs) if docs else 0)

        if docs:
            await vector_store_manager.set_collection(collection_name)
            await vector_store_manager.add_documents(docs)
            retriever = await vector_store_manager.get_retriever()
            qa_pipeline_manager.create_pipeline(retriever)
            # os.remove(file_path)
            
            return {
                "message": f"File '{filename}' processed and added to the knowledge base with collection name '{collection_name}'.",
                "num_docs": len(docs)
            }
        else:
            logger.warning("No documents produced from file '%s'", filename)
            return {"message": f"File '{filename}' could not be processed or is empty."}
    except Exception as e:
        logger.exception("Failed to process file '%s'", filename)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(question: Question):
    try:
        logger.info("Received question: %s", question.query)
        qa_pipeline = qa_pipeline_manager.get_pipeline()
        if qa_pipeline is None:
            logger.error("QA pipeline requested before initialization.")
            raise HTTPException(status_code=500, detail="QA pipeline not initialized. Please process a file first.")

        result = await asyncio.to_thread(qa_pipeline.invoke, question.query)
        logger.info("Successfully invoked QA pipeline.")

        if isinstance(result, str):
            return {"answer": result}
        elif isinstance(result, dict) and "result" in result:
            return {"answer": result["result"]}
        else:
            return {"answer": str(result)}

    except Exception as e:
        logger.exception("Failed to answer question: %s", question.query)
        raise HTTPException(status_code=500, detail=str(e))
