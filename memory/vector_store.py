# memory/vector_store.py

import os
import chromadb
from datetime import datetime
from typing import Optional
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    """
    Long-term memory for ARA-1.
    Uses free local embeddings — no API key needed.
    Model: all-MiniLM-L6-v2 (runs on your Mac)
    """
    
    def __init__(self):
        # Set up ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )
        
        # Create or connect to research collection
        self.collection = self.client.get_or_create_collection(
            name="financial_research",
            metadata={
                "description": "ARA-1 long-term research memory"
            }
        )
        
        # Free local embedding model
        # Downloads once, runs locally forever after
        print("[Memory] Loading embedding model...")
        self.embedding_model = SentenceTransformer(
            'all-MiniLM-L6-v2'
        )
        print("[Memory] Embedding model loaded")
        print(f"[Memory] Current records: {self.collection.count()}")
    
    def _generate_embedding(self, text: str) -> list:
        """
        Convert text into a vector using local model.
        Free, fast, runs on your Mac.
        """
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def store(self,
              content: str,
              ticker: str,
              source_type: str,
              confidence: float = 0.8,
              verified: bool = False) -> str:
        """
        Store research finding in long-term memory.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        doc_id = f"{ticker}-{source_type}-{timestamp}"
        
        embedding = self._generate_embedding(content)
        
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "ticker": ticker,
                "source_type": source_type,
                "date": datetime.now().isoformat(),
                "confidence": str(confidence),
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
        Search memory for relevant past research.
        Always call this before external API calls.
        """
        # If memory is empty return empty list
        if self.collection.count() == 0:
            print("[Memory] Memory is empty — no past research found")
            return []
        
        query_embedding = self._generate_embedding(query)
        
        where_filter = None
        if ticker:
            where_filter = {"ticker": ticker}
        
        actual_top_k = min(
            top_k, 
            self.collection.count()
        )
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_top_k,
            where=where_filter
        )
        
        formatted = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": round(
                        1 - results["distances"][0][i], 3
                    ) if results.get("distances") else 0
                })
        
        print(f"[Memory] Found {len(formatted)} relevant memories")
        return formatted
    
    def get_stats(self) -> dict:
        return {
            "total_records": self.collection.count(),
            "collection_name": self.collection.name
        }


# Global instance
vector_store = VectorStore()