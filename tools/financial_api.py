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
                return get_financial_data_yfinance(
                    ticker, statement_type, period, years
                )
        
        elif response.status_code == 403:
            print(f"[FMP] API limit reached, using stub")
            return get_financial_data_yfinance(
                ticker, statement_type, period, years
            )
        
        else:
            print(f"[FMP] API returned {response.status_code}")
            return get_financial_data_yfinance(
                ticker, statement_type, period, years
            )
    
    except Exception as e:
        print(f"[FMP] Error: {e}, using stub")
        return get_financial_data_yfinance(
            ticker, statement_type, period, years
        )

def get_financial_data_yfinance(
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
def get_financial_data_yfinance(
    ticker: str,
    statement_type: str = "income",
    period: str = "annual",
    years: int = 3
) -> dict:
    """
    Yahoo Finance — completely free, no API key needed.
    Used as fallback when FMP fails or hits limit.
    """
    
    print(f"[Yahoo Finance] Getting {statement_type} for {ticker}...")
    
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if statement_type == "income":
            data = stock.financials
        elif statement_type == "balance":
            data = stock.balance_sheet
        elif statement_type == "cashflow":
            data = stock.cashflow
        elif statement_type == "ratios":
            # Build ratios from info
            return {
                "ticker": ticker,
                "statement_type": "ratios",
                "latest_period": "current",
                "key_metrics": {
                    "pe_ratio": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "profit_margin": info.get("profitMargins"),
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                    "debt_to_equity": info.get("debtToEquity"),
                    "current_ratio": info.get("currentRatio"),
                    "revenue_growth": info.get("revenueGrowth"),
                    "earnings_growth": info.get("earningsGrowth")
                },
                "company_info": {
                    "market_cap": info.get("marketCap"),
                    "52_week_high": info.get("fiftyTwoWeekHigh"),
                    "52_week_low": info.get("fiftyTwoWeekLow"),
                    "analyst_target": info.get("targetMeanPrice")
                },
                "source": "Yahoo Finance via yfinance (real, free)"
            }
        else:
            data = stock.financials
        
        if data is not None and not data.empty:
            latest_col = data.columns[0]
            latest_data = data[latest_col].to_dict()
            
            # Clean the data
            clean_metrics = {}
            for k, v in latest_data.items():
                try:
                    if v and str(v) != 'nan':
                        clean_metrics[str(k)] = float(v)
                except:
                    pass
            
            # Add key summary metrics
            summary = {
                "ticker": ticker,
                "statement_type": statement_type,
                "latest_period": str(latest_col)[:10],
                "key_metrics": clean_metrics,
                "company_name": info.get("longName", ticker),
                "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap"),
                "source": "Yahoo Finance via yfinance (real, free)"
            }
            
            # Add income-specific highlights
            if statement_type == "income":
                summary["highlights"] = {
                    "revenue": info.get("totalRevenue"),
                    "gross_profit": info.get("grossProfits"),
                    "ebitda": info.get("ebitda"),
                    "net_income": info.get("netIncomeToCommon"),
                    "earnings_growth": info.get("earningsGrowth"),
                    "revenue_growth": info.get("revenueGrowth")
                }
            
            return summary
        
        else:
            print(f"[Yahoo Finance] No data returned for {ticker}")
            return get_financial_data_yfinance(
                ticker, statement_type, period, years
            )
    
    except Exception as e:
        print(f"[Yahoo Finance] Error: {e}")
        return get_financial_data_yfinance(
            ticker, statement_type, period, years
        )