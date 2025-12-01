from abc import ABC, abstractmethod
from typing import Any, Sequence


class DataLoaderInterface(ABC):
    @abstractmethod
    def load(self, file_path: str) -> Sequence[Any]:
        """Load an uploaded document and return its contents."""
        raise NotImplementedError
