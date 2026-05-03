# synthesis/conflict_resolver.py

from agent.llm import llm_client

# Source reliability tiers
# Lower number = more reliable
SOURCE_TIERS = {
    "10-K": 1,
    "10-Q": 1,
    "8-K": 1,
    "DEF 14A": 1,
    "sec_filing_search": 1,
    "financial_data_api": 2,
    "fmp": 2,
    "bloomberg": 2,
    "earnings_transcript": 3,
    "earnings_call": 3,
    "web_search": 4,
    "news": 4,
    "tavily": 4,
    "news_sentiment": 4,
    "social_media": 5,
    "unknown": 4
}

class ConflictResolver:
    """
    Detects and resolves conflicts between data sources.
    
    When two sources report different numbers for the
    same metric, this component decides which to trust
    and documents the decision transparently.
    
    Example conflict:
    - financial_data_api says Apple revenue = $391B
    - web_search says Apple revenue = $385B
    Resolution: Use financial_data_api (Tier 2 vs Tier 4)
    """
    
    def __init__(self):
        self.conflicts_found = []
        self.resolutions = []
        print("[Conflict Resolver] Initialized")
    
    def check_for_conflict(self,
                            metric: str,
                            value1: float,
                            source1: str,
                            value2: float,
                            source2: str) -> dict:
        """
        Check if two values for same metric conflict.
        Conflict threshold: more than 5% difference.
        """
        
        if value1 == 0 or value2 == 0:
            return {"conflict": False}
        
        # Calculate percentage difference
        diff_pct = abs(value1 - value2) / max(
            abs(value1), abs(value2)
        ) * 100
        
        if diff_pct > 5:
            conflict = {
                "metric": metric,
                "value1": value1,
                "source1": source1,
                "value2": value2,
                "source2": source2,
                "difference_pct": round(diff_pct, 2),
                "conflict": True
            }
            
            self.conflicts_found.append(conflict)
            print(f"[Conflict] Found: {metric} — {diff_pct:.1f}% difference")
            print(f"  {source1}: {value1}")
            print(f"  {source2}: {value2}")
            
            return conflict
        
        return {"conflict": False}
    
    def resolve_conflict(self,
                          metric: str,
                          value1: float,
                          source1: str,
                          value2: float,
                          source2: str) -> dict:
        """
        Resolve conflict using source reliability hierarchy.
        Always documents the resolution transparently.
        """
        
        tier1 = self._get_source_tier(source1)
        tier2 = self._get_source_tier(source2)
        
        # Lower tier number = more reliable
        if tier1 <= tier2:
            chosen_value = value1
            chosen_source = source1
            rejected_value = value2
            rejected_source = source2
            reason = f"{source1} (Tier {tier1}) is more reliable than {source2} (Tier {tier2})"
        else:
            chosen_value = value2
            chosen_source = source2
            rejected_value = value1
            rejected_source = source1
            reason = f"{source2} (Tier {tier2}) is more reliable than {source1} (Tier {tier1})"
        
        resolution = {
            "metric": metric,
            "chosen_value": chosen_value,
            "chosen_source": chosen_source,
            "rejected_value": rejected_value,
            "rejected_source": rejected_source,
            "resolution_reason": reason,
            "both_values": f"{source1}: {value1}, {source2}: {value2}"
        }
        
        self.resolutions.append(resolution)
        print(f"[Conflict] Resolved: Using {chosen_source} value: {chosen_value}")
        
        return resolution
    
    def check_temporal_conflict(self,
                                 value1: float,
                                 date1: str,
                                 value2: float,
                                 date2: str) -> dict:
        """
        Sometimes conflict is just different time periods.
        Check if dates explain the discrepancy.
        """
        if date1 != date2:
            return {
                "temporal_conflict": True,
                "explanation": f"Different periods: {date1} vs {date2}. Not a true conflict.",
                "recommendation": f"Use {date1} value if most recent, or specify both with dates"
            }
        
        return {"temporal_conflict": False}
    
    def get_conflict_summary(self) -> str:
        """
        Summary of all conflicts found and resolved.
        This goes into the report methodology section.
        """
        if not self.conflicts_found:
            return "No significant data conflicts detected across sources."
        
        summary = f"**Data Conflicts Identified:** {len(self.conflicts_found)}\n\n"
        
        for i, conflict in enumerate(self.conflicts_found, 1):
            resolution = self.resolutions[i-1] if i <= len(self.resolutions) else None
            
            summary += f"**Conflict {i}: {conflict['metric']}**\n"
            summary += f"- {conflict['source1']}: {conflict['value1']}\n"
            summary += f"- {conflict['source2']}: {conflict['value2']}\n"
            summary += f"- Difference: {conflict['difference_pct']}%\n"
            
            if resolution:
                summary += f"- Resolution: {resolution['resolution_reason']}\n"
                summary += f"- Value used: {resolution['chosen_value']}\n"
            
            summary += "\n"
        
        return summary
    
    def _get_source_tier(self, source: str) -> int:
        """Get reliability tier for a source"""
        source_lower = source.lower()
        
        for key, tier in SOURCE_TIERS.items():
            if key.lower() in source_lower:
                return tier
        
        return 4  # Default to Tier 4 if unknown


# Global instance
conflict_resolver = ConflictResolver()