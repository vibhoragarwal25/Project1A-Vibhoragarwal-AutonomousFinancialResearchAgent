from dotenv import load_dotenv
import os

load_dotenv()

class Settings:LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    FMP_KEY = os.getenv("FMP_API_KEY")
    TAVILY_KEY = os.getenv("TAVILY_API_KEY")MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", 20))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 5))CHROMA_PATH = "./chroma_db"
    COLLECTION_NAME = "financial_research"

settings = Settings()
