# tools/earnings.py
def get_earnings_transcript(ticker: str, quarter: str, year: int) -> dict:
    return {
        "ticker": ticker, "quarter": quarter, "year": year,
        "transcript": f"Q{quarter} {year} earnings call transcript for {ticker}. Management highlighted strong performance across key segments. [STUB]",
        "speakers": ["CEO", "CFO", "Analyst Q&A"],
        "source": "Earnings Transcript (stub)"
    }