# tools/web_search.py

import requests
import os

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")

def web_search(
    query: str, 
    num_results: int = 10,
    date_range: str = None
) -> dict:
    """Real Tavily search implementation"""
    if not TAVILY_KEY:
        return web_search_stub(query, num_results)
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_KEY,
        "query": query,
        "max_results": num_results,
        "search_depth": "advanced"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return {
                "query": query,
                "results": data.get("results", []),
                "answer": data.get("answer", "")
            }
        return {"error": f"Tavily returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def web_search_stub(query: str, num_results: int = 10,
                    date_range: str = None) -> dict:
    return {
        "query": query,
        "results": [
            {
                "url": "https://example.com/article1",
                "title": f"Analysis: {query}",
                "snippet": f"Recent developments regarding {query} show significant activity in the market.",
                "date": "2024-11-01"
            }
        ],
        "source": "Web Search (stub)"
    }