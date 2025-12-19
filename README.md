# RAG Powered Question-Answering System

This project is a Retrieval-Augmented Generation (RAG) based Question-Answering system. It uses a language model to answer questions based on the content of a provided PDF or text file. The system is built with a FastAPI backend and a Next.js frontend.

## Features

- **File Upload:** Upload PDF or text files to be used as the knowledge base.
- **Question-Answering:** Ask questions about the content of the uploaded file and get detailed answers.
- **Dynamic UI:** The user interface is built with Next.js + React and provides a ChatGPT-style experience.
- **Markdown, LaTeX & Code Rendering:** Responses render Markdown, KaTeX equations, tables, and syntax-highlighted code blocks.
- **Responsive Layout:** Optimised for both desktop and mobile viewing.

## Installation

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.9+
- Pip (or Conda)
- Node.js 18+

### Setup Using [uv](https://docs.astral.sh/uv/getting-started/installation/)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ghost-141/PDF-QA-System.git
    cd PDF-QA-System
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    uv sync
    .\.venv\Scripts\activate   # Windows
    source .venv/bin/activate  # macOS / Linux
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Setup Using Conda

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ghost-141/PDF-QA-System.git
    cd PDF-QA-System
    ```

2.  **Create a Conda environment:**
    ```bash
    conda create --name pdf_qa python=3.9.23
    conda activate pdf_qa
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install the frontend dependencies:**
    ```bash
    cd frontend
    npm install
    ```

### GPU Support (NVIDIA)

For GPU acceleration, you need to install PyTorch with CUDA support. Make sure you have the correct NVIDIA drivers and CUDA Toolkit version installed.

1.  **Check your NVIDIA driver and CUDA version:**
    You can check your NVIDIA driver version by running `nvidia-smi` in your terminal. This will also show the highest version of CUDA that is supported.

2.  **Install PyTorch with CUDA:**
    Visit the [PyTorch website](https://pytorch.org/get-started/locally/) to find the correct command for your specific CUDA version. For example, to install PyTorch with CUDA 12.6, you would run:
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
    ```

    **Note:** Using a version of PyTorch with CUDA support is essential for running the model on an NVIDIA GPU. If you do not have a compatible GPU, the embedding model will run on the CPU, which will be significantly slower while processing the pdf.

### Configuration

Create a `.env` file in the **root** of the project and add your keys:

```
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL_NAME=openai/gpt-oss-120b   # optional override
```

Uploads are stored in `data/raw` and the vector database persists in `data/vector_db` (created automatically).

## Running the Application

Start the backend and frontend in separate terminals.

### Backend (FastAPI)

```bash
uvicorn backend.main:app --reload
```

The API is available at `http://localhost:8000`.

### Frontend (Next.js)

```bash
cd frontend
npm install      # first time only
npm run dev
```

The UI is available at `http://localhost:3000`.

> **Tip:** Set `NEXT_PUBLIC_API_URL` inside `frontend/.env.local` if your API is not running on the default host/port.

## Project Structure (relevant parts)

- `backend/main.py`: FastAPI app factory and CORS setup.
- `backend/api/`: API routers for files and QA (`/upload-file`, `/process-file`, `/ask`).
- `backend/services/`: File processing, vector store management, QA pipeline, uploads.
- `backend/data/`: Runtime data; `data/raw` for uploads, `data/vector_db` for Chroma persistence.
- `frontend/`: Next.js client.

## Usage

1.  **Upload a file:** Use the upload card in the UI to select a PDF or text file.
2.  **Process the file:** Click "Upload & Process" to push the file to the backend and populate the vector store.
3.  **Ask a question:** Type your question in the chat composer. Responses appear in a ChatGPT-style transcript with full formatting.

## API Documentation

The FastAPI backend provides the following endpoints:

- **`POST /upload-file`**: Accepts a multipart file upload and stores it in `data/raw`.
    - **Form Field:** `file` (`UploadFile`, required)
    - **Success Response:** `{"filename": "<stored-filename>"}`
- **`POST /process-file`**: Processes a previously uploaded file.
    - **Query Parameter:** `filename` (string, required)
    - **Success Response:** `{"message": "File '<filename>' processed...", "num_docs": <number>}`
    - **Error Response:** `{"detail": "File '<filename>' not found..."}`
- **`POST /ask`**: Asks a question to the model.
    - **Request Body:** `{"query": "<your-question>"}`
    - **Success Response:** `{"answer": "<model-answer>"}`
    - **Error Response:** `{"detail": "QA pipeline not initialized..."}`


## Libraries & Frameworks Used

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [React](https://react.dev/)
- [LangChain](https://www.langchain.com/)
- [ChromaDB](https://www.trychroma.com/)
- [PyPDF / PyMuPDF](https://pypdf.readthedocs.io/en/stable/)

## Upcoming Features

- Support for Bangla Languge
- Process Images and Complex Pdf
- Support for different documents
- Local llm support 
