# tools/__init__.py

from tools.tool_registry import registry, ToolSchema
from tools.sec_edgar import search_sec_filings
from tools.financial_api import get_financial_data
from tools.web_search import web_search
from tools.news_sentiment import analyze_news_sentiment
from tools.calculator import run_calculation
from tools.earnings import get_earnings_transcript
from tools.company_profile import get_company_profile
from tools.peer_comparison import compare_peers
from tools.fact_checker import check_fact
from tools.report_gen import generate_report
from memory.vector_store import VectorStore

_vs = VectorStore()

def register_all_tools():
    """Register all 12 tools dynamically"""
    
    tools_config = [
        ToolSchema(
            name="sec_filing_search",
            description="Search and retrieve SEC EDGAR filings for a publicly traded US company. Use when you need official regulatory disclosures including annual reports (10-K), quarterly reports (10-Q), material event reports (8-K). Most reliable source for financial data.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker e.g. AAPL MSFT TSLA"
                    },
                    "filing_type": {
                        "type": "string",
                        "enum": ["10-K", "10-Q", "8-K", "DEF 14A"]
                    },
                    "year": {
                        "type": "integer",
                        "description": "Filing year, defaults to most recent"
                    }
                },
                "required": ["ticker", "filing_type"]
            },
            function=search_sec_filings,
            fallbacks=["web_search", "financial_data_api"]
        ),
        ToolSchema(
            name="financial_data_api",
            description="Retrieve structured financial data including income statement, balance sheet, cash flow, and key ratios. Use for precise numerical financial data. More accurate than web search for numbers.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "statement_type": {
                        "type": "string",
                        "enum": [
                            "income", "balance",
                            "cashflow", "ratios"
                        ]
                    },
                    "period": {
                        "type": "string",
                        "enum": ["annual", "quarterly"]
                    },
                    "years": {
                        "type": "integer",
                        "default": 3
                    }
                },
                "required": ["ticker", "statement_type"]
            },
            function=get_financial_data,
            fallbacks=["sec_filing_search", "web_search"]
        ),
        ToolSchema(
            name="web_search",
            description="Search the web for current news, analysis, and commentary. Use for recent developments, qualitative information, and news not in structured databases. Do not use for numerical financial data.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {
                        "type": "integer",
                        "default": 5
                    },
                    "date_range": {"type": "string"}
                },
                "required": ["query"]
            },
            function=web_search,
            fallbacks=["news_sentiment"]
        ),
        ToolSchema(
            name="news_sentiment",
            description="Analyze sentiment of recent news about a company using NLP. Returns positive/negative/neutral sentiment scores. Use to gauge market perception.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_articles": {
                        "type": "integer",
                        "default": 10
                    },
                    "lookback_days": {
                        "type": "integer",
                        "default": 30
                    }
                },
                "required": ["query"]
            },
            function=analyze_news_sentiment,
            fallbacks=["web_search"]
        ),
        ToolSchema(
            name="earnings_transcript",
            description="Retrieve earnings call transcript for a specific company and quarter. Use to understand management commentary, forward guidance, and analyst Q&A. Reveals what management says vs what financials show.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "quarter": {
                        "type": "string",
                        "enum": ["Q1", "Q2", "Q3", "Q4"]
                    },
                    "year": {"type": "integer"}
                },
                "required": ["ticker", "quarter", "year"]
            },
            function=get_earnings_transcript,
            fallbacks=["web_search", "sec_filing_search"]
        ),
        ToolSchema(
            name="company_profile",
            description="Retrieve basic company information including sector, industry, market cap, CEO, employees, and business description. Use at the start of any company research.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            },
            function=get_company_profile,
            fallbacks=["web_search"]
        ),
        ToolSchema(
            name="peer_comparison",
            description="Identify peer companies and compare key financial metrics. Use for competitive analysis, industry benchmarking, and relative valuation.",
            parameters={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "num_peers": {
                        "type": "integer",
                        "default": 5
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["ticker"]
            },
            function=compare_peers,
            fallbacks=["financial_data_api", "web_search"]
        ),
        ToolSchema(
            name="vector_db_search",
            description="Search long-term memory for previously researched information. ALWAYS call this first before making external API calls. If the company was researched before, use that data.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {
                        "type": "integer",
                        "default": 5
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Filter by company ticker"
                    }
                },
                "required": ["query"]
            },
            function=lambda query, top_k=5, ticker=None: {
                "results": _vs.search(query, top_k, ticker),
                "count": len(_vs.search(query, top_k, ticker))
            },
            fallbacks=[]
        ),
        ToolSchema(
            name="vector_db_store",
            description="Store research findings in long-term memory. Call after gathering important data to enable future retrieval.",
            parameters={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "ticker": {"type": "string"},
                    "source_type": {"type": "string"}
                },
                "required": ["content", "ticker", "source_type"]
            },
            function=lambda content, ticker, source_type: {
                "doc_id": _vs.store(content, ticker, source_type)
            },
            fallbacks=[]
        ),
        ToolSchema(
            name="fact_checker",
            description="Cross-reference a specific claim against multiple sources to verify accuracy. Use for any numerical claim before including in final report.",
            parameters={
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "string",
                        "description": "The specific claim to verify"
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["claim"]
            },
            function=check_fact,
            fallbacks=["web_search"]
        ),
        ToolSchema(
            name="calculation_engine",
            description="Perform financial calculations including growth rates, margins, CAGR, PE ratio, and DCF. Always use this for original calculations rather than estimating.",
            parameters={
                "type": "object",
                "properties": {
                    "calculation_type": {
                        "type": "string",
                        "enum": [
                            "growth_rate", "margin",
                            "cagr", "pe_ratio", "dcf"
                        ]
                    },
                    "inputs": {
                        "type": "object",
                        "description": "Input values for calculation"
                    }
                },
                "required": ["calculation_type", "inputs"]
            },
            function=run_calculation,
            fallbacks=[]
        ),
        ToolSchema(
            name="report_generator",
            description="Format researched data into a structured investment research report. Call this as the final step after all data is gathered and synthesized.",
            parameters={
                "type": "object",
                "properties": {
                    "template": {
                        "type": "string",
                        "enum": [
                            "company_profile",
                            "earnings_analysis",
                            "risk_assessment",
                            "full_report"
                        ]
                    },
                    "sections": {"type": "object"},
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["template", "sections", "sources"]
            },
            function=generate_report,
            fallbacks=[]
        )
    ]
    
    for tool in tools_config:
        registry.register(tool)
    
    print(f"[Registry] {len(tools_config)} tools registered")
    return registry


register_all_tools()