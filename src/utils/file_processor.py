from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class FileProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def process(self):
        if self.file_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(self.file_path)
        elif self.file_path.lower().endswith(".txt"):
            loader = TextLoader(self.file_path, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type: {self.file_path}")
        
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
        return text_splitter.split_documents(documents)
