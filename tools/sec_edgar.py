# tools/sec_edgar.py

import requests
import time
from typing import Optional

def search_sec_filings(
    ticker: str, 
    filing_type: str, 
    year: Optional[int] = None
) -> dict:
    """
    Real EDGAR implementation — free, no API key needed
    Rate limit: 10 req/sec, mandatory User-Agent header
    """
    headers = {
        "User-Agent": "ARA-1 Research Agent ara1@quantumedge.com",
        "Accept-Encoding": "gzip, deflate",
    }
    
    # Step 1: Get CIK number for ticker
    search_url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2020-01-01&enddt=2025-01-01&forms={filing_type}"
    
    try:
        response = requests.get(search_url, headers=headers)
        time.sleep(0.1)  # Respect rate limit
        
        if response.status_code == 200:
            data = response.json()
            return {
                "ticker": ticker,
                "filing_type": filing_type,
                "filings": data.get("hits", {}).get("hits", [])[:3],
                "total_found": data.get("hits", {}).get("total", {}).get("value", 0)
            }
        else:
            return {"error": f"EDGAR returned {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}


# STUB version for testing without API calls
def search_sec_filings_stub(
    ticker: str,
    filing_type: str, 
    year: Optional[int] = None
) -> dict:
    """Returns realistic mock data for testing"""
    return {
        "ticker": ticker,
        "filing_type": filing_type,
        "filing_date": "2024-10-30",
        "accession_number": "0000320193-24-000123",
        "filing_text": f"""
        ANNUAL REPORT ON FORM 10-K
        Company: {ticker}
        
        RISK FACTORS:
        1. Competition risk: Intense competition in all markets
        2. Regulatory risk: Subject to evolving regulations
        3. Technology risk: Rapid technology changes
        
        FINANCIAL HIGHLIGHTS:
        Revenue: $100 billion
        Operating Income: $25 billion
        Net Income: $20 billion
        """,
        "source": "SEC EDGAR (stub)"
    }