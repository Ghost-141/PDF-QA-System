from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class FileProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def process(self):
        logger.info("Starting file processing for %s", self.file_path)

        try:
            if self.file_path.lower().endswith(".pdf"):
                loader = PyPDFLoader(self.file_path)
                logger.info("Initialized PyPDFLoader for %s", self.file_path)
            elif self.file_path.lower().endswith(".txt"):
                loader = TextLoader(self.file_path, encoding="utf-8")
                logger.info("Initialized TextLoader for %s", self.file_path)
            else:
                logger.error("Unsupported file type encountered: %s", self.file_path)
                raise ValueError(f"Unsupported file type: {self.file_path}")

            documents = loader.load()
            logger.info("Loaded %d raw document segments from %s", len(documents), self.file_path)

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
            chunks = text_splitter.split_documents(documents)
            logger.info("Split documents into %d chunks for %s", len(chunks), self.file_path)
            return chunks
        except Exception:
            logger.exception("Failed while processing file %s", self.file_path)
            raise
