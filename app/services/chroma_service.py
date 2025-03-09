import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from typing import List
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class ChromaService:
    def __init__(self):
        # Initialize ChromaDB Persistent Client
        self.client = chromadb.PersistentClient(path="./chromadb")

        # OpenAI embedding function (replace with your embedding library)
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),  # Load API key from environment
            model_name="text-embedding-3-small"
        )

        # Initialize or create the "books" collection
        self.collection = self.client.get_or_create_collection(
            name="books",
            embedding_function=self.embedding_function
        )

    def add_book(self, book_id: str, title: str, description: str):
        """
        Add a book's embedding to the collection.
        """
        self.collection.upsert(
            ids=[book_id],
            documents=[f"{title}. {description}"],
            metadatas=[{"title": title, "description": description}]
        )

    def search_books(self, query: str, n_results: int = 3, distance_threshold: float = 0.8) -> List[dict]:
        """
        Search for similar books based on a query with a similarity threshold.

        :param query: Query text for semantic search.
        :param n_results: Maximum number of results to retrieve.
        :param distance_threshold: Maximum similarity score to include a result.
        :return: List of metadata dictionaries for matching books.
        """
        results = self.collection.query(
            query_texts=[query],  # Single query
            n_results=n_results
        )

        # Flatten distances and metadata (results["distances"] and results["metadatas"] are lists of lists)
        metadatas = results["metadatas"][0] 
        distances = results["distances"][0]  

        # Combine metadata and distances for filtering
        filtered_results = [
            {**metadata, "distance": distance}  # Add distance to each metadata entry
            for metadata, distance in zip(metadatas, distances)
            if distance <= distance_threshold  # Filter based on distance threshold
        ]

        return filtered_results

    def generate_natural_language_response(self, query: str, search_results: List[dict]) -> str:
        """
        Use GPT-4o-mini-2024-07-18 to generate a concise natural language summary of the search results.
        """
        if not search_results:
            return f"No similar books found for the query: '{query}'."

        # Construct a concise OpenAI prompt
        prompt = (
            f"Summarize the following books based on the query '{query}'. Include the number of books found and a brief description of each:\n\n"
            f"{search_results}\n\n"
            "Generate a concise summary."
        )

        # Call OpenAI API
        openai.api_key = os.getenv("OPENAI_API_KEY")
        client = openai.Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are an assistant whose job is to summarize book search results."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,  # Reduce max tokens for a concise response
            temperature=0.2  # Low temperature for deterministic results
        )
        return response.choices[0].message.content