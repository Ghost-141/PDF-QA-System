import requests
import os
import re
import streamlit as st 
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Powered QA System", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(UPLOAD_DIR, exist_ok=True)

API_URL = os.getenv("API_URL", "http://localhost:8000")

def clear_upload_directory():
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.error(f"Failed to delete {file_path}. Reason: {e}")




def render_mixed_content(text):
    """
    Render mixed content in Streamlit:
    - Markdown text
    - LaTeX equations ($...$ inline, $...$ block)
    - Code in any language (triple backticks)
    """
    code_pattern = r"(```.*?```)"
    code_parts = re.split(code_pattern, text, flags=re.DOTALL)

    for code_part in code_parts:
        # Explicit triple-backtick code block
        if code_part.startswith("```") and code_part.endswith("```"):
            first_line = code_part.split("\n")[0][3:].strip()
            code_content = "\n".join(code_part.split("\n")[1:-1])
            st.code(code_content, language=first_line or None)
            st.markdown("")  

        # Markdown + LaTeX
        else:
            block_latex_pattern = r"(\$\$.*?\$\$)"
            block_parts = re.split(block_latex_pattern, code_part, flags=re.DOTALL)
            for block in block_parts:
                if block.startswith("$") and block.endswith("$"):
                    st.latex(block.strip("$"))
                    st.markdown("")  # spacing after block
                else:
                    inline_parts = re.split(r"(\$.*?\$)", block)
                    for part in inline_parts:
                        if part.startswith("$") and part.endswith("$"):
                            st.latex(part.strip("$"))
                        else:
                            paragraphs = part.split("\n\n")
                            for p in paragraphs:
                                if p.strip():
                                    st.markdown(p)
                                    st.markdown("")

uploaded_file = st.sidebar.file_uploader("📂 Upload a PDF or Text file", type=["pdf", "txt"])
if uploaded_file is not None:
    clear_upload_directory()
    st.sidebar.success(f"Uploaded: {uploaded_file.name}")
    save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.sidebar.button("Process File"):
        with st.spinner("Processing file..."):
            try:
                response = requests.post(
                    f"{API_URL}/process-file?filename={uploaded_file.name}"
                )
                if response.status_code == 200:
                    st.sidebar.success("File processed successfully!")
                else:
                    st.sidebar.error("Failed to process file.")
            except Exception as e:
                st.error(f"Error: {e}")


question = st.chat_input("Ask me anything")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"query": question}
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "I could not find the answer in the provided context.")
                    render_mixed_content(answer)
                else:
                    st.error("Failed to get answer from the backend.")
            except Exception as e:
                st.error(f"Error: {e}")
