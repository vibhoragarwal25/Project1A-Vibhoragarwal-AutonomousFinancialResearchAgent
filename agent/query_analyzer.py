# agent/query_analyzer.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class QueryType(str, Enum):
    COMPANY_PROFILE    = "company_profile"
    EARNINGS_ANALYSIS  = "earnings_analysis"
    RISK_ASSESSMENT    = "risk_assessment"
    SECTOR_ANALYSIS    = "sector_analysis"
    COMPARISON         = "comparison"
    AMBIGUOUS          = "ambiguous"

class ComplexityLevel(str, Enum):
    LOW    = "low"     # single company, single topic
    MEDIUM = "medium"  # multi-topic or needs synthesis
    HIGH   = "high"    # multi-company, contradictions, memory needed

class AmbiguityLevel(str, Enum):
    CLEAR     = "clear"
    MODERATE  = "moderate"   # some assumptions needed
    HIGH      = "high"       # clarification required

@dataclass
class QueryAnalysis:
    original_query: str
    query_type: QueryType
    complexity: ComplexityLevel
    ambiguity: AmbiguityLevel
    detected_tickers: list[str]
    detected_companies: list[str]
    is_temporal_sensitive: bool
    assumptions: list[str]
    clarifying_questions: list[str]
    urgency_hint: str  # standard / urgent / critical


class QueryAnalyzer:
    
    KNOWN_TICKERS = [
        "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN",
        "NVDA", "META", "NFLX", "JPM", "GS", "PLTR",
        "HDFC", "INFY", "TCS", "RELIANCE"
    ]

    COMPANY_ALIASES = {
        "apple": "AAPL", "microsoft": "MSFT", "tesla": "TSLA",
        "google": "GOOGL", "alphabet": "GOOGL", "amazon": "AMZN",
        "nvidia": "NVDA", "meta": "META", "netflix": "NFLX",
        "jpmorgan": "JPM", "jp morgan": "JPM", "goldman": "GS",
        "palantir": "PLTR"
    }

    def analyze(self, query: str) -> QueryAnalysis:
        q = query.lower().strip()

        query_type      = self._detect_type(q)
        complexity      = self._detect_complexity(q)
        ambiguity       = self._detect_ambiguity(q, query_type)
        tickers         = self._extract_tickers(query)
        companies       = self._extract_companies(q)
        temporal        = self._is_temporal_sensitive(q)
        assumptions     = self._generate_assumptions(q, query_type, tickers, companies)
        questions       = self._generate_clarifying_questions(q, ambiguity, query_type)
        urgency         = self._detect_urgency(q)

        return QueryAnalysis(
            original_query=query,
            query_type=query_type,
            complexity=complexity,
            ambiguity=ambiguity,
            detected_tickers=tickers,
            detected_companies=companies,
            is_temporal_sensitive=temporal,
            assumptions=assumptions,
            clarifying_questions=questions,
            urgency_hint=urgency
        )

    # ── private helpers ──────────────────────────────────────────

    def _detect_type(self, q: str) -> QueryType:
        if any(w in q for w in ["earnings", "quarterly", "revenue", "profit", "eps"]):
            return QueryType.EARNINGS_ANALYSIS
        if any(w in q for w in ["risk", "threat", "challenge", "danger", "vulnerability"]):
            return QueryType.RISK_ASSESSMENT
        if any(w in q for w in ["compare", "versus", "vs", "competitive", "comparison"]):
            return QueryType.COMPARISON
        if any(w in q for w in ["sector", "industry", "theme", "trend", "landscape"]):
            return QueryType.SECTOR_ANALYSIS
        if any(w in q for w in ["profile", "overview", "about", "what is", "who is"]):
            return QueryType.COMPANY_PROFILE
        if len(q.split()) <= 6:   # very short = likely ambiguous
            return QueryType.AMBIGUOUS
        return QueryType.COMPANY_PROFILE

    def _detect_complexity(self, q: str) -> ComplexityLevel:
        company_count = sum(1 for alias in self.COMPANY_ALIASES if alias in q)
        ticker_count  = sum(1 for t in self.KNOWN_TICKERS if t in q.upper())

        if company_count + ticker_count >= 3:
            return ComplexityLevel.HIGH
        if any(w in q for w in ["contradiction", "conflict", "despite", "however", "themes", "cross"]):
            return ComplexityLevel.HIGH
        if company_count + ticker_count == 2 or any(w in q for w in ["compare", "versus", "sector"]):
            return ComplexityLevel.MEDIUM
        return ComplexityLevel.LOW

    def _detect_ambiguity(self, q: str, qtype: QueryType) -> AmbiguityLevel:
        if qtype == QueryType.AMBIGUOUS:
            return AmbiguityLevel.HIGH

        vague_words = ["banks", "tech", "market", "stocks", "companies", "things"]
        if any(w in q for w in vague_words) and len(q.split()) <= 8:
            return AmbiguityLevel.HIGH

        if not self._extract_tickers(q) and not any(a in q for a in self.COMPANY_ALIASES):
            return AmbiguityLevel.MODERATE

        return AmbiguityLevel.CLEAR

    def _extract_tickers(self, query: str) -> list[str]:
        words = query.upper().split()
        return [w.strip(".,?!") for w in words if w.strip(".,?!") in self.KNOWN_TICKERS]

    def _extract_companies(self, q: str) -> list[str]:
        found = []
        for alias, ticker in self.COMPANY_ALIASES.items():
            if alias in q:
                found.append(f"{alias.title()} ({ticker})")
        return found

    def _is_temporal_sensitive(self, q: str) -> bool:
        keywords = ["latest", "recent", "current", "today", "now",
                    "this quarter", "this year", "acquisition", "merger", "breaking"]
        return any(k in q for k in keywords)

    def _generate_assumptions(self, q: str, qtype: QueryType,
                               tickers: list, companies: list) -> list[str]:
        assumptions = []

        if not tickers and not companies:
            if "bank" in q:
                assumptions.append("Assuming query refers to major US banks (JPM, GS, BAC)")
            elif "tech" in q:
                assumptions.append("Assuming query refers to large-cap US tech companies")

        if qtype == QueryType.EARNINGS_ANALYSIS:
            assumptions.append("Assuming most recent available quarter")

        if "amazon" in q and ("aws" not in q and "cloud" not in q):
            assumptions.append("Assuming Amazon refers to the full company (AMZN), not just AWS")

        return assumptions

    def _generate_clarifying_questions(self, q: str,
                                        ambiguity: AmbiguityLevel,
                                        qtype: QueryType) -> list[str]:
        questions = []
        if ambiguity == AmbiguityLevel.HIGH:
            if "bank" in q:
                questions.append("Which banks? (US majors, Indian banks, investment banks, regional banks?)")
                questions.append("What time period? (current quarter, full year, historical trend?)")
            elif "market" in q:
                questions.append("Which market? (equity, credit, commodities, a specific sector?)")
            else:
                questions.append("Could you specify the company or sector you're interested in?")
                questions.append("What type of analysis? (financial, risk, competitive, sector)")

        if ambiguity == AmbiguityLevel.MODERATE:
            if qtype == QueryType.COMPANY_PROFILE:
                questions.append("Should this cover financial performance, risks, or both?")

        return questions

    def _detect_urgency(self, q: str) -> str:
        if any(w in q for w in ["urgent", "asap", "immediately", "breaking", "critical"]):
            return "critical"
        if any(w in q for w in ["quick", "brief", "summary", "fast"]):
            return "urgent"
        return "standard"


# singleton
query_analyzer = QueryAnalyzer()