# memory/__init__.py

from memory.vector_store import VectorStore
from memory.context_manager import ContextManager
from memory.episodic import EpisodicMemory

vector_store = VectorStore()
context_manager = ContextManager()
episodic_memory = EpisodicMemory()