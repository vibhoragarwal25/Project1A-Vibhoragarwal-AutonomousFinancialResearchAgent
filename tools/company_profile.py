# tools/company_profile.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

FMP_KEY = os.getenv("FMP_API_KEY", "demo")

def get_company_profile(ticker: str) -> dict:
    """
    Real company profile from FMP API.
    Returns sector, industry, market cap, executives,
    description, and key facts.
    """
    
    print(f"[Company Profile] Getting profile for {ticker}...")
    
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}"
    params = {"apikey": FMP_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                profile = data[0]
                
                return {
                    "ticker": ticker,
                    "company_name": profile.get("companyName"),
                    "sector": profile.get("sector"),
                    "industry": profile.get("industry"),
                    "market_cap": profile.get("mktCap"),
                    "employees": profile.get("fullTimeEmployees"),
                    "ceo": profile.get("ceo"),
                    "website": profile.get("website"),
                    "description": profile.get("description", "")[:500],
                    "exchange": profile.get("exchangeShortName"),
                    "ipo_date": profile.get("ipoDate"),
                    "country": profile.get("country"),
                    "currency": profile.get("currency"),
                    "source": "Financial Modeling Prep (real)"
                }
        
        print(f"[Company Profile] API failed, using stub")
        return get_company_profile_stub(ticker)
        
    except Exception as e:
        print(f"[Company Profile] Error: {e}")
        return get_company_profile_stub(ticker)


def get_company_profile_stub(ticker: str) -> dict:
    """Fallback stub"""
    profiles = {
        "MSFT": {
            "company_name": "Microsoft Corporation",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 3100000000000,
            "ceo": "Satya Nadella",
            "employees": 228000,
            "description": "Microsoft develops and supports software, services, devices and solutions worldwide."
        },
        "AAPL": {
            "company_name": "Apple Inc",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 3500000000000,
            "ceo": "Tim Cook",
            "employees": 164000,
            "description": "Apple designs, manufactures and markets smartphones, computers and tablets."
        },
        "TSLA": {
            "company_name": "Tesla Inc",
            "sector": "Consumer Cyclical",
            "industry": "Auto Manufacturers",
            "market_cap": 800000000000,
            "ceo": "Elon Musk",
            "employees": 127855,
            "description": "Tesla designs and manufactures electric vehicles and energy solutions."
        },
        "NVDA": {
            "company_name": "NVIDIA Corporation",
            "sector": "Technology",
            "industry": "Semiconductors",
            "market_cap": 2800000000000,
            "ceo": "Jensen Huang",
            "employees": 29600,
            "description": "NVIDIA designs graphics processing units and system on chip units."
        }
    }
    
    profile = profiles.get(ticker, {
        "company_name": f"{ticker} Corporation",
        "sector": "Technology",
        "industry": "Software",
        "market_cap": 100000000000,
        "ceo": "Unknown",
        "employees": 10000,
        "description": f"{ticker} is a publicly traded company."
    })
    
    profile["ticker"] = ticker
    profile["source"] = "Company Profile (stub)"
    return profile