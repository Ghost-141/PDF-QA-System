from typing import Optional

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    query: str


class UploadResponse(BaseModel):
    filename: str


class ProcessFileResponse(BaseModel):
    message: str
    num_docs: Optional[int] = None


class AnswerResponse(BaseModel):
    answer: str
