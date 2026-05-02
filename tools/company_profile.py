# tools/company_profile.py
def get_company_profile(ticker: str) -> dict:
    return {
        "ticker": ticker,
        "name": f"{ticker} Corporation",
        "sector": "Technology",
        "industry": "Software",
        "market_cap": 3000000000000,
        "ceo": "John Smith",
        "employees": 150000,
        "description": f"{ticker} is a leading technology company. [STUB]",
        "source": "Company Profile (stub)"
    }