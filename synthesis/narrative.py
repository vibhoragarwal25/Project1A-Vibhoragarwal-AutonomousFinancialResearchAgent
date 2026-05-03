# synthesis/narrative.py

from agent.llm import llm_client

class NarrativeEngine:
    """
    Connects data points from different sources into
    a coherent analytical story.
    
    A simple agent just lists facts.
    A sophisticated agent connects them into insights.
    
    Example:
    Facts: Revenue grew 15%, management optimistic,
           3 news articles report customer contract losses
    
    Narrative: Revenue growth is backward-looking and
    may not be sustainable. Management optimism may not
    fully account for recent customer losses.
    This divergence is itself an analytical finding.
    """
    
    def __init__(self):
        print("[Narrative] Engine initialized")
    
    def generate_insight(self,
                          data_points: list,
                          topic: str) -> str:
        """
        Generate analytical insight by connecting
        multiple data points from different sources.
        
        data_points: list of dicts with 'fact' and 'source'
        topic: what we are analyzing
        """
        
        if not data_points:
            return "Insufficient data for narrative generation"
        
        # Format data points
        facts_text = "\n".join([
            f"- {dp.get('fact', '')} (Source: {dp.get('source', 'unknown')})"
            for dp in data_points
        ])
        
        insight = llm_client.chat(
            system_prompt="""You are a senior financial analyst.
            Your job is to connect data points into insights.
            
            Go beyond restating facts.
            Look for:
            - Trends across time periods
            - Contradictions between sentiment and data
            - Leading indicators vs lagging indicators
            - What management says vs what numbers show
            - Industry context for company performance
            
            Be specific. Use numbers. Cite sources.""",
            user_message=f"""
            Topic: {topic}
            
            Data points gathered:
            {facts_text}
            
            Generate 2-3 original analytical insights 
            that connect these data points:
            """,
            max_tokens=600
        )
        
        return insight
    
    def check_sentiment_fact_alignment(self,
                                        sentiment: str,
                                        key_metric: float,
                                        metric_name: str,
                                        benchmark: float) -> dict:
        """
        Compare sentiment (qualitative) with facts (quantitative).
        Misalignment is an important analytical finding.
        
        Example:
        Sentiment: overwhelmingly positive news
        Fact: operating margins declining
        Finding: Sentiment-fact divergence — flag for review
        """
        
        aligned = True
        finding = ""
        
        positive_sentiment = sentiment.lower() in [
            "positive", "bullish", "optimistic"
        ]
        negative_sentiment = sentiment.lower() in [
            "negative", "bearish", "pessimistic"
        ]
        
        metric_positive = key_metric >= benchmark
        
        if positive_sentiment and not metric_positive:
            aligned = False
            finding = f"DIVERGENCE DETECTED: News sentiment is {sentiment} but {metric_name} ({key_metric:.2f}) is below benchmark ({benchmark:.2f}). This divergence warrants further investigation."
        
        elif negative_sentiment and metric_positive:
            aligned = False
            finding = f"DIVERGENCE DETECTED: News sentiment is {sentiment} but {metric_name} ({key_metric:.2f}) exceeds benchmark ({benchmark:.2f}). Market may be undervaluing this company."
        
        else:
            finding = f"Sentiment and fundamentals are aligned. {sentiment} sentiment consistent with {metric_name} performance."
        
        return {
            "aligned": aligned,
            "sentiment": sentiment,
            "metric_name": metric_name,
            "metric_value": key_metric,
            "benchmark": benchmark,
            "finding": finding
        }
    
    def build_narrative_thread(self,
                                theme: str,
                                evidence: list) -> str:
        """
        Build a coherent narrative thread around a theme.
        Each thread has a thesis supported by evidence
        from multiple sources.
        """
        
        evidence_text = "\n".join([
            f"- {e}" for e in evidence
        ])
        
        narrative = llm_client.chat(
            system_prompt="""You are writing an investment
            research narrative. Build a coherent analytical
            thread with a clear thesis supported by evidence.
            
            Format:
            THESIS: [one clear analytical claim]
            EVIDENCE: [supporting points]
            IMPLICATION: [what this means for investors]""",
            user_message=f"""
            Theme: {theme}
            Evidence: {evidence_text}
            
            Build the narrative thread:
            """,
            max_tokens=400
        )
        
        return narrative


# Global instance
narrative_engine = NarrativeEngine()