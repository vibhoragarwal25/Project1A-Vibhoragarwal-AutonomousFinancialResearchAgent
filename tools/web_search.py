# tools/web_search.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")

def web_search(
    query: str,
    num_results: int = 5,
    date_range: str = None
) -> dict:
    """
    Real Tavily search — 1000 free searches per month.
    Designed specifically for AI agent use.
    Returns clean, structured results.
    """
    
    print(f"[Tavily] Searching: {query[:60]}...")
    
    if not TAVILY_KEY or TAVILY_KEY == "your_tavily_key_here":
        print("[Tavily] No API key, using stub")
        return web_search_stub(query, num_results)
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_KEY,
                "query": query,
                "max_results": num_results,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            for r in data.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:300],
                    "published_date": r.get("published_date", "")
                })
            
            return {
                "query": query,
                "answer": data.get("answer", ""),
                "results": results,
                "total_results": len(results),
                "source": "Tavily Search (real)"
            }
        
        else:
            print(f"[Tavily] API returned {response.status_code}")
            return web_search_stub(query, num_results)
    
    except Exception as e:
        print(f"[Tavily] Error: {e}")
        return web_search_stub(query, num_results)


def web_search_stub(
    query: str,
    num_results: int = 5,
    date_range: str = None
) -> dict:
    """Fallback stub"""
    return {
        "query": query,
        "answer": f"Based on available information about {query}: Recent developments show continued activity in this area with multiple stakeholders engaged.",
        "results": [
            {
                "title": f"Analysis: {query}",
                "url": "https://finance.yahoo.com",
                "snippet": f"Recent analysis of {query} indicates significant market activity. Analysts remain cautiously optimistic about near-term prospects.",
                "published_date": "2024-11-01"
            }
        ],
        "source": "Web Search (stub fallback)"
    }