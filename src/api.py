from fastapi import FastAPI, HTTPException, Query
import os
import re
from pydantic import BaseModel
from src.utils.file_processor import FileProcessor
from src.utils.datastore import VectorStoreManager
from src.utils.retriever import QAPipelineManager

# Folder for uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Q/A based RAG API",
    description="API for question-answering using RAG pipeline",
    version="1.0.0"
)

vector_store_manager = VectorStoreManager()
qa_pipeline_manager = QAPipelineManager()

class Question(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "Bangla RAG API is up!"}

@app.post("/process-file")
async def process_file(filename: str = Query(..., description="Filename to load from data/raw")):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found in {UPLOAD_DIR}")

    try:
        vector_store_manager.clean_database()

        collection_name = os.path.splitext(filename)[0]
        collection_name = re.sub(r'\W+', '_', collection_name).lower()
        collection_name = collection_name[:63]

        file_processor = FileProcessor(file_path)
        docs = file_processor.process()

        if docs:
            vector_store_manager.set_collection(collection_name)
            vector_store_manager.add_documents(docs)
            qa_pipeline_manager.create_pipeline(vector_store_manager.get_retriever())
            os.remove(file_path)
            
            return {
                "message": f"File '{filename}' processed and added to the knowledge base with collection name '{collection_name}'.",
                "num_docs": len(docs)
            }
        else:
            return {"message": f"File '{filename}' could not be processed or is empty."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(question: Question):
    try:
        qa_pipeline = qa_pipeline_manager.get_pipeline()
        if qa_pipeline is None:
            raise HTTPException(status_code=500, detail="QA pipeline not initialized. Please process a file first.")

        result = qa_pipeline.invoke(question.query)

        if isinstance(result, str):
            return {"answer": result}
        elif isinstance(result, dict) and "result" in result:
            return {"answer": result["result"]}
        else:
            return {"answer": str(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
