# tools/financial_api.py

import requests
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

FMP_KEY = os.getenv("FMP_API_KEY", "demo")
BASE_URL = "https://financialmodelingprep.com/api/v3"

def get_financial_data(
    ticker: str,
    statement_type: str = "income",
    period: str = "annual",
    years: int = 3
) -> dict:
    """
    Real FMP API — 250 free requests per day.
    Covers income statement, balance sheet, cash flow, ratios.
    """
    
    print(f"[FMP] Getting {statement_type} for {ticker}...")
    
    endpoint_map = {
        "income": "income-statement",
        "balance": "balance-sheet-statement",
        "cashflow": "cash-flow-statement",
        "ratios": "ratios"
    }
    
    endpoint = endpoint_map.get(statement_type, "income-statement")
    url = f"{BASE_URL}/{endpoint}/{ticker}"
    
    params = {
        "period": period,
        "limit": years,
        "apikey": FMP_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                # Extract key metrics from first year
                latest = data[0]
                
                # Build clean summary
                summary = {
                    "ticker": ticker,
                    "statement_type": statement_type,
                    "period": period,
                    "latest_period": latest.get("date", "Unknown"),
                    "data": data[:years]
                }
                
                # Add key metrics based on statement type
                if statement_type == "income":
                    summary["key_metrics"] = {
                        "revenue": latest.get("revenue"),
                        "gross_profit": latest.get("grossProfit"),
                        "operating_income": latest.get("operatingIncome"),
                        "net_income": latest.get("netIncome"),
                        "eps": latest.get("eps"),
                        "revenue_growth": latest.get("revenueGrowth")
                    }
                elif statement_type == "ratios":
                    summary["key_metrics"] = {
                        "pe_ratio": latest.get("priceEarningsRatio"),
                        "roe": latest.get("returnOnEquity"),
                        "roa": latest.get("returnOnAssets"),
                        "debt_to_equity": latest.get("debtEquityRatio"),
                        "current_ratio": latest.get("currentRatio"),
                        "profit_margin": latest.get("netProfitMargin")
                    }
                
                summary["source"] = "Financial Modeling Prep (real)"
                return summary
            
            else:
                print(f"[FMP] No data returned for {ticker}")
                return get_financial_data_stub(
                    ticker, statement_type, period, years
                )
        
        elif response.status_code == 403:
            print(f"[FMP] API limit reached, using stub")
            return get_financial_data_stub(
                ticker, statement_type, period, years
            )
        
        else:
            print(f"[FMP] API returned {response.status_code}")
            return get_financial_data_stub(
                ticker, statement_type, period, years
            )
    
    except Exception as e:
        print(f"[FMP] Error: {e}, using stub")
        return get_financial_data_stub(
            ticker, statement_type, period, years
        )


def get_financial_data_stub(
    ticker: str,
    statement_type: str = "income",
    period: str = "annual",
    years: int = 3
) -> dict:
    """Fallback stub"""
    return {
        "ticker": ticker,
        "statement_type": statement_type,
        "key_metrics": {
            "revenue": 391035000000,
            "gross_profit": 170782000000,
            "operating_income": 123216000000,
            "net_income": 93736000000,
            "eps": 6.11
        },
        "source": "Financial Data (stub fallback)"
    }