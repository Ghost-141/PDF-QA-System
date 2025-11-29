import asyncio

from fastapi import APIRouter, Depends, HTTPException

from backend.core.dependency import get_qa_pipeline_manager
from backend.models.api_models import AnswerResponse, QuestionRequest
from backend.services.qa_service import QAPipelineManager
from backend.utils.logging_config import get_logger

router = APIRouter(tags=["qa"])

logger = get_logger(__name__)


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    question: QuestionRequest,
    qa_pipeline_manager: QAPipelineManager = Depends(get_qa_pipeline_manager),
):
    try:
        logger.info("Received question: %s", question.query)
        qa_pipeline = qa_pipeline_manager.get_pipeline()
        if qa_pipeline is None:
            logger.error("QA pipeline requested before initialization.")
            raise HTTPException(status_code=500, detail="QA pipeline not initialized. Please process a file first.")

        result = await asyncio.to_thread(qa_pipeline.invoke, question.query)
        logger.info("Successfully invoked QA pipeline.")

        if isinstance(result, str):
            return AnswerResponse(answer=result)
        if isinstance(result, dict) and "result" in result:
            return AnswerResponse(answer=result["result"])
        return AnswerResponse(answer=str(result))

    except Exception as exc:
        logger.exception("Failed to answer question: %s", question.query)
        raise HTTPException(status_code=500, detail=str(exc))
