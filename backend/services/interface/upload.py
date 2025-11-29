from abc import ABC, abstractmethod
from typing import Protocol

from fastapi import UploadFile


class UploadServiceInterface(ABC):
    @abstractmethod
    async def save(self, uploaded_file: UploadFile) -> str:
        """
        Persist an uploaded file and return its absolute path.
        """
        raise NotImplementedError


class FilePathResolver(Protocol):
    def __call__(self, filename: str) -> str:
        ...
