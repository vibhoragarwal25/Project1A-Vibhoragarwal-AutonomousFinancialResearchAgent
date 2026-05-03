# agent/disambiguation.py

from agent.query_analyzer import QueryAnalysis, AmbiguityLevel, query_analyzer
from agent.llm import llm_client


class DisambiguationEngine:

    def process(self, query: str) -> dict:
        """
        Returns a dict with:
          - analysis       : QueryAnalysis object
          - refined_query  : the query ready for the agent to use
          - assumptions    : list of documented assumptions
          - questions      : clarifying questions (if any)
          - should_proceed : True = proceed, False = need user input
          - urgency        : urgency level string
        """
        analysis = query_analyzer.analyze(query)

        if analysis.ambiguity == AmbiguityLevel.HIGH:
            # Try to auto-resolve with LLM before giving up
            resolved = self._llm_resolve(query, analysis)
            if resolved["confidence"] == "high":
                return {
                    "analysis": analysis,
                    "refined_query": resolved["refined_query"],
                    "assumptions": analysis.assumptions + resolved["assumptions"],
                    "questions": [],
                    "should_proceed": True,
                    "urgency": analysis.urgency_hint,
                }
            # Cannot resolve — surface questions
            return {
                "analysis": analysis,
                "refined_query": query,
                "assumptions": analysis.assumptions,
                "questions": analysis.clarifying_questions,
                "should_proceed": False,
                "urgency": analysis.urgency_hint,
            }

        # MODERATE or CLEAR — document assumptions and proceed
        refined = self._build_refined_query(query, analysis)
        return {
            "analysis": analysis,
            "refined_query": refined,
            "assumptions": analysis.assumptions,
            "questions": analysis.clarifying_questions,
            "should_proceed": True,
            "urgency": analysis.urgency_hint,
        }

    # ── private helpers ──────────────────────────────────────────

    def _llm_resolve(self, query: str, analysis: QueryAnalysis) -> dict:
        """Ask the LLM to interpret an ambiguous query."""
        prompt = f"""You are a financial research analyst. A user submitted this vague query:
"{query}"

Based on context, provide:
1. Your most likely interpretation
2. A refined, specific version of the query
3. Any assumptions you are making
4. Your confidence level (high/medium/low) that your interpretation is correct

Respond in this exact format:
INTERPRETATION: <one sentence>
REFINED_QUERY: <specific query>
ASSUMPTIONS: <comma-separated list>
CONFIDENCE: <high|medium|low>"""

        response = llm_client.chat(
            system_prompt="You are a precise financial research query interpreter.",
            user_message=prompt,
            max_tokens=400
        )

        return self._parse_llm_resolve(response)

    def _parse_llm_resolve(self, response: str) -> dict:
        lines = response.strip().split("\n")
        result = {
            "refined_query": "",
            "assumptions": [],
            "confidence": "medium"
        }
        for line in lines:
            if line.startswith("REFINED_QUERY:"):
                result["refined_query"] = line.replace("REFINED_QUERY:", "").strip()
            elif line.startswith("ASSUMPTIONS:"):
                raw = line.replace("ASSUMPTIONS:", "").strip()
                result["assumptions"] = [a.strip() for a in raw.split(",") if a.strip()]
            elif line.startswith("CONFIDENCE:"):
                result["confidence"] = line.replace("CONFIDENCE:", "").strip().lower()
        return result

    def _build_refined_query(self, query: str, analysis: QueryAnalysis) -> str:
        """Append documented assumptions to the query so the agent sees them."""
        if not analysis.assumptions:
            return query
        assumption_text = "; ".join(analysis.assumptions)
        return f"{query} [Assumptions: {assumption_text}]"

    def handle_edge_cases(self, query: str, analysis: QueryAnalysis) -> Optional[str]:
        """
        Returns a warning message for known edge cases, or None if all clear.
        """
        q = query.lower()

        # Private company — no SEC filings
        private_signals = ["private", "unlisted", "not listed", "pre-ipo"]
        if any(s in q for s in private_signals):
            return ("⚠️ This appears to be a private company. "
                    "SEC filing tools will be unavailable. "
                    "Will rely on web search and news sources only.")

        # Very new / recently IPO'd
        if any(s in q for s in ["ipo", "newly listed", "just went public", "recent ipo"]):
            return ("⚠️ Newly IPO'd company detected. "
                    "Limited historical data available. "
                    "Will flag data gaps in the report.")

        # Rate-of-change detection
        if analysis.is_temporal_sensitive:
            return ("⚠️ Query involves rapidly changing circumstances. "
                    "All data will be tagged with retrieval timestamps. "
                    "Report will include a temporal sensitivity disclaimer.")

        return None


# ── Rate-of-change detector (standalone utility) ─────────────────

def detect_rate_of_change(gathered_data: str) -> list[str]:
    """
    Scan gathered data for signals that circumstances are changing rapidly.
    Returns a list of warning strings.
    """
    warnings = []
    signals = {
        "acquisition": "Company may be mid-acquisition — valuations and structure may change.",
        "merger": "Merger activity detected — financials may not reflect post-merger entity.",
        "bankruptcy": "Bankruptcy signals detected — data reliability may be impacted.",
        "restructuring": "Restructuring underway — historical financials may not be comparable.",
        "leadership change": "Recent leadership change — forward guidance may shift.",
        "sec investigation": "Regulatory investigation signals — extra verification recommended.",
        "restatement": "Financial restatement detected — treat historical figures with caution.",
    }
    data_lower = gathered_data.lower()
    for keyword, warning in signals.items():
        if keyword in data_lower:
            warnings.append(f"⚠️ TEMPORAL FLAG — {warning}")
    return warnings


# singleton
disambiguation_engine = DisambiguationEngine()