from abc import ABC, abstractmethod
from typing import Any


class QAPipelineInterface(ABC):
    @abstractmethod
    def create_pipeline(self, retriever: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_pipeline(self) -> Any:
        raise NotImplementedError
