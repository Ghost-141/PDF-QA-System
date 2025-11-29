from typing import Optional

from fastapi import HTTPException
from langchain.chains import RetrievalQA

from backend.core.config import settings
from backend.services.interface.qa import QAPipelineInterface
from backend.system_prompts.prompt_v1 import QA_PROMPT
from backend.utils.groq_client import get_groq_chat
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class QAPipelineManager(QAPipelineInterface):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.groq_api_key
        self.model_name = model_name or settings.default_model

        try:
            self.chat = get_groq_chat(model_name=self.model_name, api_key=self.api_key)
        except Exception as exc:
            logger.exception("Failed to create ChatGroq client.")
            raise HTTPException(status_code=500, detail=str(exc))
        self.qa_pipeline = None

    def create_pipeline(self, retriever):
        logger.info("Creating QA retrieval pipeline.")
        self.qa_pipeline = RetrievalQA.from_chain_type(
            llm=self.chat,
            retriever=retriever,
            chain_type_kwargs={"prompt": QA_PROMPT},
        )
        logger.info("QA retrieval pipeline initialized successfully.")

    def get_pipeline(self):
        logger.info("Returning QA pipeline (initialized=%s)", self.qa_pipeline is not None)
        return self.qa_pipeline
