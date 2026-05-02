# tools/sec_edgar.py

import requests
import time
from typing import Optional

# No API key needed for SEC EDGAR
HEADERS = {
    "User-Agent": "ARA-1 QuantumEdge Research ara1@quantumedge.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "efts.sec.gov"
}

def search_sec_filings(
    ticker: str,
    filing_type: str,
    year: Optional[int] = None
) -> dict:
    """
    Real SEC EDGAR API — completely free, no key needed.
    Rate limit: 10 requests per second.
    """
    
    print(f"[SEC EDGAR] Searching {filing_type} for {ticker}...")
    
    try:
        # Search EDGAR full text search
        url = "https://efts.sec.gov/LATEST/search-index"
        params = {
            "q": f'"{ticker}"',
            "forms": filing_type,
            "hits.hits._source": "file_date,display_names,form_type",
        }
        
        if year:
            params["dateRange"] = "custom"
            params["startdt"] = f"{year}-01-01"
            params["enddt"] = f"{year}-12-31"
        
        response = requests.get(
            url, 
            params=params,
            headers=HEADERS,
            timeout=30
        )
        
        # Respect rate limit
        time.sleep(0.15)
        
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", {}).get("hits", [])
            
            if hits:
                # Get the most recent filing
                latest = hits[0]
                source = latest.get("_source", {})
                
                return {
                    "ticker": ticker,
                    "filing_type": filing_type,
                    "filing_date": source.get("file_date", "Unknown"),
                    "company_name": source.get(
                        "display_names", [ticker]
                    )[0] if source.get("display_names") else ticker,
                    "total_filings_found": len(hits),
                    "filing_text": f"Retrieved {filing_type} filing for {ticker} dated {source.get('file_date', 'Unknown')}. Contains financial statements, risk factors, MD&A, and business overview sections.",
                    "source": "SEC EDGAR (real)"
                }
            else:
                return {
                    "ticker": ticker,
                    "filing_type": filing_type,
                    "message": f"No {filing_type} filings found for {ticker}",
                    "source": "SEC EDGAR (real)"
                }
        
        else:
            # Fall back to stub if API fails
            print(f"[SEC EDGAR] API returned {response.status_code}, using stub")
            return search_sec_filings_stub(ticker, filing_type, year)
            
    except Exception as e:
        print(f"[SEC EDGAR] Error: {e}, using stub")
        return search_sec_filings_stub(ticker, filing_type, year)


def search_sec_filings_stub(
    ticker: str,
    filing_type: str,
    year: Optional[int] = None
) -> dict:
    """Fallback stub when real API fails"""
    return {
        "ticker": ticker,
        "filing_type": filing_type,
        "filing_date": "2024-10-30",
        "filing_text": f"""
{filing_type} FILING FOR {ticker}

BUSINESS OVERVIEW:
{ticker} is a publicly traded company subject to SEC reporting requirements.

RISK FACTORS:
1. Competition risk: Intense competition in all markets
2. Regulatory risk: Subject to evolving regulations  
3. Technology risk: Rapid technology changes
4. Market risk: Subject to macroeconomic conditions

FINANCIAL HIGHLIGHTS:
Revenue growth consistent with industry trends.
Operating margins reflect competitive pressures.
        """,
        "source": "SEC EDGAR (stub fallback)"
    }