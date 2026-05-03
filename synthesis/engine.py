# synthesis/engine.py

from synthesis.conflict_resolver import ConflictResolver
from synthesis.narrative import NarrativeEngine
from agent.llm import llm_client

class SynthesisEngine:
    """
    Combines all gathered data into professional
    investment research reports.
    
    This is the most sophisticated component of ARA-1.
    It does what makes research valuable:
    - Identifies agreements across sources
    - Resolves conflicts transparently
    - Generates original analytical insights
    - Produces coherent narrative
    """
    
    def __init__(self):
        self.conflict_resolver = ConflictResolver()
        self.narrative_engine = NarrativeEngine()
        print("[Synthesis] Engine initialized")
    
    def synthesize(self,
                    query: str,
                    gathered_data: list,
                    key_findings: list = None) -> str:
        """
        Main synthesis function.
        
        gathered_data: list of tool results
        key_findings: important findings from context manager
        """
        
        print(f"[Synthesis] Synthesizing {len(gathered_data)} data points...")
        
        # Step 1: Identify agreements
        agreements = self._find_agreements(gathered_data)
        
        # Step 2: Identify and resolve conflicts
        conflict_summary = self.conflict_resolver.get_conflict_summary()
        
        # Step 3: Generate narrative insights
        insights = self._generate_insights(
            query, gathered_data, key_findings
        )
        
        # Step 4: Build final report
        report = self._build_report(
            query=query,
            gathered_data=gathered_data,
            agreements=agreements,
            conflict_summary=conflict_summary,
            insights=insights,
            key_findings=key_findings
        )
        
        return report
    
    def _find_agreements(self, gathered_data: list) -> str:
        """
        Identify where multiple sources agree.
        Agreement = higher confidence in the finding.
        """
        if not gathered_data:
            return "Insufficient data for agreement analysis"
        
        data_text = "\n".join([
            str(d)[:300] for d in gathered_data[:5]
        ])
        
        agreements = llm_client.chat(
            system_prompt="""Identify where multiple data 
            sources agree on the same facts or trends.
            List 3-5 points of agreement with sources.""",
            user_message=f"Find agreements in: {data_text}",
            max_tokens=400
        )
        
        return agreements
    
    def _generate_insights(self,
                            query: str,
                            gathered_data: list,
                            key_findings: list = None) -> str:
        """
        Generate original analytical insights.
        Goes beyond restating retrieved facts.
        """
        
        data_summary = "\n".join([
            str(d)[:200] for d in gathered_data[:8]
        ])
        
        findings_text = ""
        if key_findings:
            findings_text = "\nKey findings:\n" + "\n".join([
                f"- {f.get('finding', '')[:100]}"
                for f in key_findings[:5]
            ])
        
        insights = llm_client.chat(
            system_prompt="""You are a senior financial analyst.
            Generate original insights that go beyond 
            restating the data. Connect trends, identify
            patterns, flag anomalies.
            
            Aim for 3 non-obvious insights.""",
            user_message=f"""
            Research topic: {query}
            
            Data gathered:
            {data_summary}
            {findings_text}
            
            Generate original analytical insights:
            """,
            max_tokens=600
        )
        
        return insights
    
    def _build_report(self,
                       query: str,
                       gathered_data: list,
                       agreements: str,
                       conflict_summary: str,
                       insights: str,
                       key_findings: list = None) -> str:
        """Build the complete research report"""
        
        data_text = "\n".join([
            str(d)[:300] for d in gathered_data[:10]
        ])
        
        report = llm_client.chat(
            system_prompt="""You are ARA-1 producing a 
            professional investment research report.
            
            Structure your report with these sections:
            1. Executive Summary
            2. Key Findings
            3. Financial Analysis  
            4. Risk Factors
            5. Analytical Insights
            6. Data Quality Notes
            
            Always cite sources. Flag uncertainty.
            Never fabricate data.""",
            user_message=f"""
            Research Query: {query}
            
            Raw Data Gathered:
            {data_text}
            
            Source Agreements:
            {agreements}
            
            Data Conflicts:
            {conflict_summary}
            
            Analytical Insights:
            {insights}
            
            Produce the complete research report:
            """,
            max_tokens=4000
        )
        
        return report


# Global instance
synthesis_engine = SynthesisEngine()