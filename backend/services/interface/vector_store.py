from abc import ABC, abstractmethod
from typing import Any


class VectorStoreInterface(ABC):
    @abstractmethod
    async def set_collection(self, collection_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_documents(self, documents: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_retriever(self, k_value: int = 6) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def clean_database(self) -> None:
        raise NotImplementedError
