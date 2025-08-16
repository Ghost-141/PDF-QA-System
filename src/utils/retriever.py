import os
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

def get_api_key():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    return groq_api_key


custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        
    """You are an AI assistant. Your task is to answer the user's question based on the provided context.

    **Output formatting rules (IMPORTANT):**

    1. **Equations**:
    - Always use LaTeX syntax for all mathematical expressions.
    - Wrap inline math in $...$ and block math in $$...$$.
    - Do not skip or alter equations.

    2. **Code**:
    - Always wrap programming code in fenced code blocks with the correct language tag.
    - Preserve indentation and syntax exactly as in the context.

    3. **Tables**:
    - Always reproduce tables in Markdown format.
    - Keep the same structure, alignment, and values.

    4. **General**:
    - Do not omit or summarize any equations, tables, or code blocks.
    - Always reproduce them fully and faithfully.
    - Provide the answer strictly based on the given context.
    - If the answer is not in the context, respond with exactly:
    "I could not find the answer in the provided context."
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
            try:
                self.api_key = get_api_key()
            except ValueError as e:
                raise HTTPException(status_code=500, detail=str(e))
        else:
            self.api_key = api_key

        self.chat = ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
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