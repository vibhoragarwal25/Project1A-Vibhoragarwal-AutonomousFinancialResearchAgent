# memory/episodic.py

import json
import os
from datetime import datetime

class EpisodicMemory:
    """
    Records what strategies worked and what didn't.
    
    This is process-level memory — not what was researched,
    but HOW the research was done successfully.
    
    Example episode:
    "For pharmaceutical risk assessment, checking FDA 
    databases via web_search before sec_filing_search 
    improved risk factor coverage significantly"
    
    Over time the agent learns which tools work best
    for which types of queries.
    """
    
    def __init__(self):
        self.episodes_file = "logs/episodic_memory.json"
        os.makedirs("logs", exist_ok=True)
        self.episodes = self._load_episodes()
        print(f"[Episodic] Loaded {len(self.episodes)} past episodes")
    
    def record_episode(self,
                       query_type: str,
                       tools_used: list,
                       tool_success_rates: dict,
                       quality_score: float,
                       key_lesson: str):
        """
        Record a completed research episode.
        
        query_type: company_profile, earnings, risk, comparison
        tools_used: list of tool names used
        tool_success_rates: dict of tool_name -> success rate
        quality_score: 0-1 score for this research session
        key_lesson: what worked or didn't work
        """
        episode = {
            "id": f"episode-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "query_type": query_type,
            "tools_used": tools_used,
            "tool_success_rates": tool_success_rates,
            "quality_score": quality_score,
            "key_lesson": key_lesson
        }
        
        self.episodes.append(episode)
        self._save_episodes()
        
        print(f"[Episodic] Episode recorded: {query_type}")
        print(f"[Episodic] Key lesson: {key_lesson[:80]}...")
        
        return episode["id"]
    
    def get_lessons_for_query_type(self, 
                                    query_type: str) -> list:
        """
        Get relevant lessons for a specific query type.
        Agent uses this to plan better research strategies.
        
        Example: Before researching earnings, get all
        lessons learned from previous earnings research.
        """
        relevant = [
            e for e in self.episodes
            if e["query_type"] == query_type
            and e["quality_score"] > 0.6
        ]
        
        # Sort by quality score — best lessons first
        relevant.sort(
            key=lambda x: x["quality_score"], 
            reverse=True
        )
        
        lessons = [e["key_lesson"] for e in relevant[:3]]
        
        if lessons:
            print(f"[Episodic] Found {len(lessons)} lessons for {query_type}")
        
        return lessons
    
    def get_best_tools_for_query(self, 
                                  query_type: str) -> list:
        """
        Which tools performed best for this query type?
        Agent uses this to prioritize tool selection.
        """
        relevant = [
            e for e in self.episodes
            if e["query_type"] == query_type
        ]
        
        if not relevant:
            return []
        
        # Aggregate tool success rates
        tool_scores = {}
        tool_counts = {}
        
        for episode in relevant:
            for tool, rate in episode.get(
                "tool_success_rates", {}
            ).items():
                if tool not in tool_scores:
                    tool_scores[tool] = 0
                    tool_counts[tool] = 0
                tool_scores[tool] += rate
                tool_counts[tool] += 1
        
        # Calculate averages
        tool_averages = {
            tool: tool_scores[tool] / tool_counts[tool]
            for tool in tool_scores
        }
        
        # Return sorted by performance
        sorted_tools = sorted(
            tool_averages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [tool for tool, score in sorted_tools]
    
    def get_summary(self) -> dict:
        """Overview of all recorded episodes"""
        if not self.episodes:
            return {
                "total_episodes": 0,
                "message": "No episodes recorded yet"
            }
        
        query_types = list(set(
            e["query_type"] for e in self.episodes
        ))
        avg_quality = sum(
            e["quality_score"] for e in self.episodes
        ) / len(self.episodes)
        
        return {
            "total_episodes": len(self.episodes),
            "query_types_covered": query_types,
            "average_quality_score": round(avg_quality, 2),
            "most_recent": self.episodes[-1]["timestamp"]
            if self.episodes else None
        }
    
    def _load_episodes(self) -> list:
        """Load episodes from file"""
        if os.path.exists(self.episodes_file):
            try:
                with open(self.episodes_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_episodes(self):
        """Save episodes to file"""
        with open(self.episodes_file, 'w') as f:
            json.dump(self.episodes, f, indent=2)


# Global instance
episodic_memory = EpisodicMemory()