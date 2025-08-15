import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

def get_api_key():
    groq_api_key = os.getenv("GROQ_API_KEY")
    return groq_api_key if groq_api_key else print("GROQ_API_KEY not found in environment variables.")


custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        """You are an AI assistant. Your task is to answer the user's question based on the provided context.

        **Output formatting rules (IMPORTANT):**

        1. **Equations**:
        - Use LaTeX syntax for all mathematical expressions.
        - Wrap inline math in single `$...$` and block math in double `$$...$$`.
        - Do **not** wrap LaTeX inside code blocks (```...```).
        - Keep LaTeX clean and syntactically valid (no extra spaces, avoid unnecessary line breaks).

        2. **Markdown**:
        - Use Markdown for text formatting (bold, italics, lists, headings).
        - Keep headings in `###` format.
        - Use bullet points `-` or numbered lists `1.` when needed.

        3. **Code**:
        - Use fenced code blocks (```language ... ```) **only** for programming code.
        - Include the language after the triple backticks if known (e.g., ```python, ```javascript).
        - Do **not** wrap plain text in code blocks.

        4. **Content Rules**:
        - Provide a detailed and comprehensive answer using only the information in the provided context.
        - If the answer is not in the context, respond with exactly:
            I could not find the answer in the provided context.
        - Never invent details or use outside knowledge.

        **Bad Example (do NOT do this):**
            
        
        Context: {context}
        Question: {question}
        Answer: """
    )
)


class QAPipelineManager:
    def __init__(self, api_key=None):
        if api_key is None:
            self.api_key = get_api_key()
            if not self.api_key:
                raise ValueError("API key is required but not provided.")
        else:
            self.api_key = api_key

        self.chat = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_retries=3,
            api_key=self.api_key,
        )
        self.qa_pipeline = None

    def create_pipeline(self, retriever):
        self.qa_pipeline = RetrievalQA.from_chain_type(
            llm=self.chat,
            retriever=retriever,
            chain_type_kwargs={"prompt": custom_prompt}
        )

    def get_pipeline(self):
        return self.qa_pipeline
