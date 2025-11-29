from abc import ABC, abstractmethod
from typing import Any, Sequence


class FileProcessorInterface(ABC):
    @abstractmethod
    def process(self) -> Sequence[Any]:
        """
        Load and split documents into chunks.
        """
        raise NotImplementedError
