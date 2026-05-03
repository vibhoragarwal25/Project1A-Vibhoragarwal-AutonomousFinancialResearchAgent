# tools/peer_comparison.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

FMP_KEY = os.getenv("FMP_API_KEY", "demo")

def compare_peers(
    ticker: str,
    num_peers: int = 5,
    metrics: list = None
) -> dict:
    """
    Find peer companies and compare key metrics.
    Used for competitive analysis in Challenges 4 and 5.
    """
    
    print(f"[Peers] Finding peers for {ticker}...")
    
    if metrics is None:
        metrics = [
            "revenue", "netIncome", "grossProfitRatio",
            "operatingIncomeRatio", "returnOnEquity"
        ]
    
    try:
        # Get peer list from FMP
        peers_url = f"https://financialmodelingprep.com/api/v4/stock_peers"
        params = {
            "symbol": ticker,
            "apikey": FMP_KEY
        }
        
        response = requests.get(
            peers_url, params=params, timeout=30
        )
        
        peer_list = []
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                peer_list = data[0].get(
                    "peersList", []
                )[:num_peers]
        
        if not peer_list:
            peer_list = _get_default_peers(ticker, num_peers)
        
        # Get financial ratios for each peer
        all_companies = [ticker] + peer_list
        comparison = {}
        
        for company in all_companies[:num_peers + 1]:
            ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{company}"
            r = requests.get(
                ratios_url,
                params={"limit": 1, "apikey": FMP_KEY},
                timeout=15
            )
            
            if r.status_code == 200:
                data = r.json()
                if data:
                    latest = data[0]
                    comparison[company] = {
                        "pe_ratio": latest.get("priceEarningsRatio"),
                        "profit_margin": latest.get("netProfitMargin"),
                        "roe": latest.get("returnOnEquity"),
                        "debt_to_equity": latest.get("debtEquityRatio"),
                        "revenue_growth": latest.get("revenueGrowth")
                    }
        
        return {
            "ticker": ticker,
            "peers": peer_list,
            "comparison_matrix": comparison,
            "metrics_used": metrics,
            "source": "Financial Modeling Prep (real)"
        }
    
    except Exception as e:
        print(f"[Peers] Error: {e}, using stub")
        return compare_peers_stub(ticker, num_peers)


def _get_default_peers(ticker: str, num_peers: int) -> list:
    """Default peer lists for common tickers"""
    peer_map = {
        "MSFT": ["AAPL", "GOOGL", "META", "AMZN"],
        "AAPL": ["MSFT", "GOOGL", "META", "SAMSUNG"],
        "TSLA": ["GM", "F", "RIVN", "NIO"],
        "NVDA": ["AMD", "INTC", "QCOM", "TSM"],
        "AMZN": ["MSFT", "GOOGL", "BABA", "WMT"],
        "GOOGL": ["MSFT", "META", "AAPL", "AMZN"]
    }
    return peer_map.get(ticker, ["MSFT", "AAPL", "GOOGL"])[:num_peers]


def compare_peers_stub(ticker: str, 
                        num_peers: int = 5) -> dict:
    """Fallback stub"""
    peers = _get_default_peers(ticker, num_peers)
    return {
        "ticker": ticker,
        "peers": peers,
        "comparison_matrix": {
            ticker: {
                "pe_ratio": 28.5,
                "profit_margin": 0.25,
                "roe": 0.35,
                "debt_to_equity": 0.5
            }
        },
        "source": "Peer Comparison (stub)"
    }