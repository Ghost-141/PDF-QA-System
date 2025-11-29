import asyncio
import shutil
from pathlib import Path
from typing import Union

from fastapi import UploadFile

from backend.services.interface.upload import UploadServiceInterface
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)


class UploadService(UploadServiceInterface):
    def __init__(self, save_dir: Union[Path, str] = "./data/raw"):
        self.save_dir = Path(save_dir)

    async def save(self, uploaded_file: UploadFile) -> str:
        """
        Persist a FastAPI UploadFile to disk asynchronously.
        """
        logger.info("Saving uploaded file '%s' to directory '%s'", uploaded_file.filename, self.save_dir)
        await asyncio.to_thread(self.save_dir.mkdir, parents=True, exist_ok=True)
        file_path = self.save_dir / uploaded_file.filename

        def _persist_file():
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(uploaded_file.file, buffer)

        try:
            await asyncio.to_thread(_persist_file)
        except Exception:
            logger.exception("Failed to persist uploaded file '%s'", uploaded_file.filename)
            raise

        abs_path = str(file_path.resolve())
        logger.info("Saved file to %s", abs_path)
        return abs_path
