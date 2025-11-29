from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.services.interface.file_processor import FileProcessorInterface
from backend.utils.logging_config import get_logger

logger = get_logger(__name__)

class FileProcessor(FileProcessorInterface):
    def __init__(self, file_path: str, chunk_size: int = 900, chunk_overlap: int = 100, page_chunk_size: int = 10):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.page_chunk_size = page_chunk_size  # To handle large PDFs in chunks of pages

    def process(self):
        logger.info("Starting file processing for %s", self.file_path)

        try:
            if self.file_path.lower().endswith(".pdf"):
                loader = PyMuPDFLoader(self.file_path, mode="page")
                logger.info("Initialized PyPDFLoader for %s", self.file_path)
            elif self.file_path.lower().endswith(".txt"):
                loader = TextLoader(self.file_path, encoding="utf-8")
                logger.info("Initialized TextLoader for %s", self.file_path)
            else:
                logger.error("Unsupported file type encountered: %s", self.file_path)
                raise ValueError(f"Unsupported file type: {self.file_path}")

            loaded_pages = loader.load()
            documents = []
            for i in range(0, len(loaded_pages), self.page_chunk_size):
                chunk = loaded_pages[i:i + self.page_chunk_size]
                documents.extend(chunk)
                logger.info("Loaded pages %d to %d", i + 1, i + len(chunk))

            logger.info("Loaded %d raw document segments from %s", len(documents), self.file_path)

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            chunks = text_splitter.split_documents(documents)
            logger.info("Split documents into %d chunks for %s", len(chunks), self.file_path)

            return chunks
        except Exception:
            logger.exception("Failed while processing file %s", self.file_path)
            raise
