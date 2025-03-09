import os
import openai
from fastapi import UploadFile

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai  import ChatOpenAI


class PdfRagService:
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        top_k: int = 3
    ):
        # Make sure OPENAI_API_KEY is set in your environment or via code
        openai.api_key = os.getenv("OPENAI_API_KEY")

        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

        self._vectorstore = None

    def get_vectorstore(self):
        return self._vectorstore

    async def create_vectorstore_from_pdf(self, file_path: str):
        """
        1) Load PDF from a file path using PyPDFLoader.
        2) Split into chunks, embed, store in in-memory Chroma.
        """
        # 1) Load PDF from disk
        pdf_loader = PyPDFLoader(file_path)
        pdf_docs = pdf_loader.load()

        # 2) Chunk the text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        docs = text_splitter.split_documents(pdf_docs)

        # 3) Create embeddings & store in Chroma in-memory
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name="pdf_collection"
        )
        self._vectorstore = vectorstore

    async def answer_query_with_vectorstore(self, question: str):
        """
        Retrieve from vectorstore & run the question through GPT-4o-mini.
        """
        if not self._vectorstore:
            raise ValueError("No PDF loaded. Please upload a PDF first.")

        # Create a retriever (top-k matches)
        retriever = self._vectorstore.as_retriever(search_kwargs={"k": self.top_k})

        # Use ChatOpenAI with gpt-4o-mini
        llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=0
        )

        # Build a retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )

        answer = qa_chain.invoke(question)
        return answer
