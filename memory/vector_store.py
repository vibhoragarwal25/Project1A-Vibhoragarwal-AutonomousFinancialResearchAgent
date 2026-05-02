# memory/vector_store.py

import os
import chromadb
from chromadb.config import Settings
from datetime import datetime
from typing import Optional
import openai
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    """
    Long-term memory for ARA-1.
    Stores and retrieves research findings across sessions.
    Uses ChromaDB locally — free, no setup needed.
    """
    
    def __init__(self):
        # Set up ChromaDB with persistent storage
        # This means memory survives between sessions
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )
        
        # Create or connect to our research collection
        self.collection = self.client.get_or_create_collection(
            name="financial_research",
            metadata={"description": "ARA-1 long-term research memory"}
        )
        
        # OpenAI client for generating embeddings
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print(f"[Memory] Vector store initialized")
        print(f"[Memory] Current records: {self.collection.count()}")
    
    def _generate_embedding(self, text: str) -> list:
        """
        Convert text into a vector (list of numbers).
        Similar texts produce similar vectors.
        This is how semantic search works.
        """
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def store(self, 
              content: str,
              ticker: str,
              source_type: str,
              confidence: float = 0.8,
              verified: bool = False) -> str:
        """
        Store a research finding in long-term memory.
        
        Example:
        store(
            content="Apple revenue grew 6% YoY to $391B in FY2024",
            ticker="AAPL",
            source_type="10-K",
            confidence=0.95,
            verified=True
        )
        """
        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        doc_id = f"{ticker}-{source_type}-{timestamp}"
        
        # Generate embedding for semantic search
        embedding = self._generate_embedding(content)
        
        # Store in ChromaDB
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "ticker": ticker,
                "source_type": source_type,
                "date": datetime.now().isoformat(),
                "confidence": confidence,
                "verified": str(verified),
                "researcher_session": f"session-{timestamp[:8]}"
            }]
        )
        
        print(f"[Memory] Stored: {doc_id}")
        return doc_id
    
    def search(self, 
               query: str,
               top_k: int = 5,
               ticker: str = None) -> list:
        """
        Search long-term memory for relevant past research.
        Always call this FIRST before making external API calls.
        
        Example:
        results = search("Apple revenue growth", ticker="AAPL")
        """
        # Generate embedding for the search query
        query_embedding = self._generate_embedding(query)
        
        # Build filter if ticker specified
        where_filter = None
        if ticker:
            where_filter = {"ticker": ticker}
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, max(1, self.collection.count())),
            where=where_filter
        )
        
        # Format results nicely
        formatted = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": 1 - results["distances"][0][i]
                    if results["distances"] else 0
                })
        
        print(f"[Memory] Search '{query[:50]}...' → {len(formatted)} results")
        return formatted
    
    def get_stats(self) -> dict:
        """Show memory statistics"""
        return {
            "total_records": self.collection.count(),
            "collection_name": self.collection.name
        }


# Global instance
vector_store = VectorStore()