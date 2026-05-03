# agent/fallback_chains.py

"""
Fallback chains for every primary tool.
When a tool fails, the agent tries these in order.

Design principle:
- Each fallback provides similar (if less precise) info
- Confidence decreases with each fallback level
- Always end with graceful degradation option

This directly implements the spec requirement:
'For each primary tool, define one or more fallback 
tools that can provide similar (if less precise) 
information'
"""

FALLBACK_CHAINS = {
    
    "sec_filing_search": [
        "web_search",           # Search for filing content online
        "financial_data_api",   # Get key metrics instead
        "vector_db_search"      # Check if we researched this before
    ],
    
    "financial_data_api": [
        "sec_filing_search",    # Extract numbers from filings
        "web_search",           # Search financial summary sites
        "vector_db_search",     # Use previously stored data
        "company_profile"       # Basic metrics as last resort
    ],
    
    "web_search": [
        "news_sentiment",       # NLP on available articles
        "vector_db_search"      # Use past research
    ],
    
    "news_sentiment": [
        "web_search",           # Raw search instead of sentiment
        "vector_db_search"      # Past sentiment analysis
    ],
    
    "earnings_transcript": [
        "web_search",           # Search for transcript excerpts
        "sec_filing_search",    # 10-Q has some similar info
        "financial_data_api"    # Just use financial numbers
    ],
    
    "company_profile": [
        "web_search",           # Search for company info
        "financial_data_api",   # Get financial profile
        "sec_filing_search"     # Extract from 10-K cover page
    ],
    
    "peer_comparison": [
        "financial_data_api",   # Get company metrics individually
        "web_search",           # Search for competitor info
        "sec_filing_search"     # Extract competitor mentions
    ],
    
    "fact_checker": [
        "web_search",           # Manual search for verification
        "sec_filing_search"     # Verify against official filings
    ],
    
    "calculation_engine": [],   # No fallback — deterministic math
    
    "report_generator": [],     # No fallback — formatting only
    
    "vector_db_search": [],     # No fallback — internal only
    
    "vector_db_store": []       # No fallback — internal only
}


def get_fallbacks(tool_name: str) -> list:
    """Get fallback chain for a tool"""
    return FALLBACK_CHAINS.get(tool_name, [])


def get_confidence_note(
    original_tool: str,
    fallback_used: str
) -> str:
    """
    Generate confidence note when fallback is used.
    This goes into the report methodology section.
    """
    
    confidence_map = {
        ("sec_filing_search", "web_search"): 
            "Web search used instead of SEC filing — data may be less authoritative",
        
        ("financial_data_api", "sec_filing_search"): 
            "Figures extracted from SEC filing — may require manual parsing verification",
        
        ("financial_data_api", "web_search"): 
            "Financial data from web search — cross-reference with SEC filing recommended",
        
        ("earnings_transcript", "web_search"): 
            "Transcript excerpts from web — may be incomplete or paraphrased",
        
        ("earnings_transcript", "sec_filing_search"): 
            "10-Q filing used as earnings transcript proxy — lacks Q&A section",
    }
    
    note = confidence_map.get(
        (original_tool, fallback_used),
        f"Fallback source {fallback_used} used instead of {original_tool} — verify critical figures"
    )
    
    return f"⚠️ DATA NOTE: {note}"