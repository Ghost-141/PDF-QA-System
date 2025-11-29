import os
from typing import Optional

from langchain_groq import ChatGroq

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


def get_groq_chat(
    model_name: str = "openai/gpt-oss-120b",
    temperature: float = 0.1,
    max_retries: int = 3,
    api_key: Optional[str] = None,
) -> ChatGroq:
    """
    Create a ChatGroq client using environment configuration.
    """
    groq_api_key = api_key or os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY is missing; cannot initialize Groq client.")
        raise ValueError("GROQ_API_KEY not found in environment variables.")

    logger.info("Initializing ChatGroq client with model '%s'.", model_name)
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        max_retries=max_retries,
        api_key=groq_api_key,
    )
