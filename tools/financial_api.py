# tools/financial_api.py

import requests
import os
from typing import Optional

FMP_KEY = os.getenv("FMP_API_KEY", "demo")

def get_financial_data(
    ticker: str,
    statement_type: str = "income",
    period: str = "annual",
    years: int = 3
) -> dict:
    """
    Real FMP implementation
    statement_type: income | balance | cashflow | ratios
    """
    endpoint_map = {
        "income": "income-statement",
        "balance": "balance-sheet-statement", 
        "cashflow": "cash-flow-statement",
        "ratios": "ratios"
    }
    
    endpoint = endpoint_map.get(statement_type, "income-statement")
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}"
    
    params = {
        "period": period,
        "limit": years,
        "apikey": FMP_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "ticker": ticker,
                "statement_type": statement_type,
                "period": period,
                "data": data
            }
        return {"error": f"FMP returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_financial_data_stub(ticker: str, statement_type: str = "income",
                             period: str = "annual", years: int = 3) -> dict:
    return {
        "ticker": ticker,
        "statement_type": statement_type,
        "data": [
            {
                "date": "2024-09-30",
                "revenue": 391035000000,
                "grossProfit": 170782000000,
                "operatingIncome": 123216000000,
                "netIncome": 93736000000,
                "eps": 6.11
            }
        ],
        "source": "Financial Data API (stub)"
    }