import requests
import os
import re
import streamlit as st 
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Powered QA System", layout="wide")

UPLOAD_DIR = "./data/raw"
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


def clean_math_text(text):
    # Remove repeated single-letter variables like "a a"
    text = re.sub(r'\b([a-zA-Z])\s+\1\b', r'\1', text)
    # Remove excessive spaces before punctuation
    text = re.sub(r'\s+,', ',', text)
    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def render_mixed_content(text):
    text = clean_math_text(text)  # 🆕 pre-cleaning step

    # Existing LaTeX normalization
    text = re.sub(r"\[\s*(.*?)\s*\]", r"$$\1$$", text, flags=re.DOTALL)
    text = re.sub(r"\\\n", "", text)
    text = re.sub(r"\s*\n\s*", " ", text)

    parts = re.split(r"(```.*?```|\$\$.*?\$\$)", text, flags=re.DOTALL)
    for part in parts:
        if part.startswith("```") and part.endswith("```"):
            lines = part.split("\n")
            language = lines[0][3:].strip() or None
            code_content = "\n".join(lines[1:-1])
            st.code(code_content, language=language)
        elif part.startswith("$$") and part.endswith("$"):
            st.latex(part.strip("$"))
        else:
            inline_parts = re.split(r"(\$.*?\$)", part)
            for ipart in inline_parts:
                if ipart.startswith("$") and ipart.endswith("$"):
                    st.latex(ipart.strip("$"))
                else:
                    paragraphs = ipart.split("\n\n")
                    for p in paragraphs:
                        if p.strip():
                            st.markdown(p)



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
