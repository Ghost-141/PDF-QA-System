from typing import Optional

from langchain_community.chat_models import ChatOllama

from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


def get_ollama_chat(
    model_name: str = "llama3.2",
    temperature: float = 0.1,
    base_url: str = "http://localhost:11434",
) -> ChatOllama:
    """
    Create a ChatOllama client to run LLMs hosted locally via Ollama.

    Parameters
    ----------
    model_name: name of the locally available Ollama model (e.g., "llama3.2" or "mistral").
    temperature: sampling temperature.
    base_url: Ollama server URL; defaults to the local daemon.
    request_timeout: optional timeout for long generations.
    """
    logger.info("Initializing ChatOllama client for model '%s' at '%s'.", model_name, base_url)
    return ChatOllama(
        model=model_name,
        temperature=temperature,
        base_url=base_url
    )
