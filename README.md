# RAG Powered Question-Answering System

This project is a Retrieval-Augmented Generation (RAG) based Question-Answering system. It uses a language model to answer questions based on the content of a provided PDF or text file. The system is built with a FastAPI backend and a Streamlit frontend.

## Features

- **File Upload:** Upload PDF or text files to be used as the knowledge base.
- **Question-Answering:** Ask questions about the content of the uploaded file and get detailed answers.
- **Dynamic UI:** The user interface is built with Streamlit and provides a chat-like experience.
- **Markdown and LaTeX Support:** The UI can render both Markdown and LaTeX, allowing for complex responses including mathematical equations.
- **Code Formatting:** Code snippets in the answers are correctly formatted and highlighted.

## Installation

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.9
- Pip or Conda

### Using Pip

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ghost-141/PDF-QA-System.git
    cd PDF-QA-System
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3.9 -m venv pdf_qa
    pdf_qa/bin/activate #for windows
    source pdf_qa\bin\activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Using Conda

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ghost-141/PDF-QA-System.git
    cd PDF-QA-System
    ```

2.  **Create a Conda environment:**
    ```bash
    conda create --name pdf_qa python=3.9
    conda activate pdf_qa
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
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

Create a `.env` file in the root directory of the project and add your Groq API key:
```
GROQ_API_KEY=your-groq-api-key
```

## Running the Application

To run the application, execute the following command in your terminal:

```bash
python main.py
```

This will open two new terminal windows: one for the FastAPI backend and one for the Streamlit frontend.

The UI will be available at `http://localhost:8501` and the API at `http://localhost:8000`.

## Usage

1.  **Upload a file:**
    Use the sidebar in the UI to upload a PDF or text file.

2.  **Process the file:**
    Click the "Process File" button to have the backend process the file and create a vector store.

3.  **Ask a question:**
    Type your question in the chat input box and press Enter. The model will use the content of the file to generate an answer.

## API Documentation

The FastAPI backend provides the following endpoints:


- **`POST /process-file`**: Processes an uploaded file.
    - **Query Parameter:** `filename` (string, required)
    - **Success Response:** `{"message": "File '<filename>' processed and added to the knowledge base...", "num_docs": <number>}`
    - **Error Response:** `{"detail": "File '<filename>' not found..."}`
- **`POST /ask`**: Asks a question to the model.
    - **Request Body:** `{"query": "<your-question>"}`
    - **Success Response:** `{"answer": "<model-answer>"}`
    - **Error Response:** `{"detail": "QA pipeline not initialized..."}`


## Libraries & Frameworks Used


- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://groq.com/)
- [ChromaDB](https://www.trychroma.com/)
- [PyPDF](https://pypdf.readthedocs.io/en/stable/)

## Upcoming Features

- Support for Bangla Languge
- Improved UI for Complex Ouput Support
- Process Images and Complex Pdf
