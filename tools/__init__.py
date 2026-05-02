# tools/__init__.py

from tools.tool_registry import registry, ToolSchema
from tools.sec_edgar import search_sec_filings_stub
from tools.financial_api import get_financial_data_stub
from tools.web_search import web_search_stub
from tools.news_sentiment import analyze_news_sentiment
from tools.calculator import run_calculation
from tools.earnings import get_earnings_transcript
from tools.company_profile import get_company_profile
from tools.peer_comparison import compare_peers
from tools.fact_checker import check_fact
from tools.report_gen import generate_report

def register_all_tools():
    """Register all tools — called at agent startup"""
    
    tools_config = [
        ToolSchema(
            name="sec_filing_search",
            description="Search and retrieve SEC EDGAR filings for a publicly traded US company. Use when you need official regulatory disclosures including annual reports (10-K), quarterly reports (10-Q), material event reports (8-K), or proxy statements (DEF 14A).",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol e.g. AAPL"},
                    "filing_type": {"type": "string", "enum": ["10-K", "10-Q", "8-K", "DEF 14A"]},
                    "year": {"type": "integer", "description": "Filing year, defaults to most recent"}
                },
                "required": ["ticker", "filing_type"]
            },
            function=search_sec_filings_stub,
            fallbacks=["web_search", "financial_data_api"]
        ),
        ToolSchema(
            name="financial_data_api",
            description="Retrieve structured financial data including income statement, balance sheet, cash flow, and key ratios. Use for precise numerical financial data rather than web search.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "statement_type": {"type": "string", 
                                      "enum": ["income", "balance", "cashflow", "ratios"]},
                    "period": {"type": "string", "enum": ["annual", "quarterly"]},
                    "years": {"type": "integer", "default": 3}
                },
                "required": ["ticker", "statement_type"]
            },
            function=get_financial_data_stub,
            fallbacks=["sec_filing_search", "web_search"]
        ),
        ToolSchema(
            name="web_search",
            description="Search the web for current news, analysis, and commentary. Use for recent developments, news, and qualitative information not available in structured databases.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer", "default": 10},
                    "date_range": {"type": "string", "description": "e.g. past_week, past_month"}
                },
                "required": ["query"]
            },
            function=web_search_stub,
            fallbacks=["news_sentiment"]
        ),
        ToolSchema(
            name="news_sentiment",
            description="Analyze sentiment of recent news about a company or topic using NLP. Returns sentiment scores and article summaries.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_articles": {"type": "integer", "default": 10},
                    "lookback_days": {"type": "integer", "default": 30}
                },
                "required": ["query"]
            },
            function=analyze_news_sentiment,
            fallbacks=["web_search"]
        ),
        ToolSchema(
            name="calculation_engine",
            description="Perform financial calculations including growth rates, margins, ratios, CAGR, and DCF. Always use this for original calculations rather than estimating.",
            parameters={
                "type": "object",
                "properties": {
                    "calculation_type": {"type": "string",
                                        "enum": ["growth_rate", "margin", "cagr", "pe_ratio", "dcf"]},
                    "inputs": {"type": "object", "description": "Input values for calculation"}
                },
                "required": ["calculation_type", "inputs"]
            },
            function=run_calculation,
            fallbacks=[]
        ),
        ToolSchema(
            name="earnings_transcript",
            description="Retrieve earnings call transcript for a specific company quarter. Use to understand management commentary, forward guidance, and analyst Q&A.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "quarter": {"type": "string", "enum": ["Q1", "Q2", "Q3", "Q4"]},
                    "year": {"type": "integer"}
                },
                "required": ["ticker", "quarter", "year"]
            },
            function=get_earnings_transcript,
            fallbacks=["web_search", "sec_filing_search"]
        ),
        ToolSchema(
            name="company_profile",
            description="Retrieve basic company information including sector, industry, market cap, key executives, and business description.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            },
            function=get_company_profile,
            fallbacks=["web_search"]
        ),
        ToolSchema(
            name="peer_comparison",
            description="Identify peer companies and retrieve comparative financial metrics. Use for competitive analysis and benchmarking.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "num_peers": {"type": "integer", "default": 5},
                    "metrics": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["ticker"]
            },
            function=compare_peers,
            fallbacks=["financial_data_api", "web_search"]
        ),
        ToolSchema(
            name="fact_checker",
            description="Cross-reference a specific claim against multiple authoritative sources to verify accuracy. Always use for numerical claims before including in final report.",
            parameters={
                "type": "object",
                "properties": {
                    "claim": {"type": "string", "description": "The specific claim to verify"},
                    "sources": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["claim"]
            },
            function=check_fact,
            fallbacks=["web_search", "financial_data_api"]
        ),
        ToolSchema(
            name="report_generator",
            description="Format researched data into a structured investment research report following a specified template.",
            parameters={
                "type": "object",
                "properties": {
                    "template": {"type": "string", 
                                "enum": ["company_profile", "earnings_analysis", 
                                        "risk_assessment", "full_report"]},
                    "sections": {"type": "object"},
                    "sources": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["template", "sections", "sources"]
            },
            function=generate_report,
            fallbacks=[]
        ),
    ]
    
    for tool in tools_config:
        registry.register(tool)
    
    print(f"[Registry] {len(tools_config)} tools registered successfully")
    return registry

# Auto-register on import
register_all_tools()