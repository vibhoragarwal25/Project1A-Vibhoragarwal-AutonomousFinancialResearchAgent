# agent/logger.py

import json
import os
from datetime import datetime

class AgentLogger:
    """
    Logs every decision, tool call, and observation.
    This creates your Trace Gallery material.
    Critical for evaluation — every action must be logged.
    """
    
    def __init__(self):
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Create session log file
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/session_{self.session_id}.json"
        self.traces = []
        
        print(f"[Logger] Session started: {self.session_id}")
        print(f"[Logger] Log file: {self.log_file}")
    
    def log_thought(self, thought: str):
        """Log agent reasoning step"""
        entry = {
            "type": "THOUGHT",
            "timestamp": datetime.now().isoformat(),
            "content": thought
        }
        self.traces.append(entry)
        print(f"[THOUGHT] {thought[:100]}...")
        self._save()
    
    def log_action(self, tool_name: str, params: dict):
        """Log tool call"""
        entry = {
            "type": "ACTION",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "params": params
        }
        self.traces.append(entry)
        print(f"[ACTION] {tool_name}({params})")
        self._save()
    
    def log_observation(self, tool_name: str, 
                        result: dict, success: bool):
        """Log tool result"""
        entry = {
            "type": "OBSERVATION",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "success": success,
            "result_preview": str(result)[:200]
        }
        self.traces.append(entry)
        status = "✅" if success else "❌"
        print(f"[OBSERVATION] {status} {tool_name} returned")
        self._save()
    
    def log_error(self, tool_name: str, 
                  error: str, fallback_used: str = None):
        """Log errors and fallbacks"""
        entry = {
            "type": "ERROR",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "error": error,
            "fallback_used": fallback_used
        }
        self.traces.append(entry)
        print(f"[ERROR] {tool_name}: {error}")
        if fallback_used:
            print(f"[FALLBACK] Using {fallback_used} instead")
        self._save()
    
    def log_synthesis(self, insight: str, sources: list):
        """Log synthesis decisions"""
        entry = {
            "type": "SYNTHESIS",
            "timestamp": datetime.now().isoformat(),
            "insight": insight,
            "sources": sources
        }
        self.traces.append(entry)
        print(f"[SYNTHESIS] {insight[:100]}...")
        self._save()
    
    def get_session_summary(self) -> dict:
        """Summary of the entire research session"""
        thoughts = len([t for t in self.traces if t["type"] == "THOUGHT"])
        actions = len([t for t in self.traces if t["type"] == "ACTION"])
        errors = len([t for t in self.traces if t["type"] == "ERROR"])
        
        return {
            "session_id": self.session_id,
            "total_steps": len(self.traces),
            "thoughts": thoughts,
            "tool_calls": actions,
            "errors": errors,
            "log_file": self.log_file
        }
    
    def _save(self):
        """Save traces to file after every entry"""
        with open(self.log_file, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "traces": self.traces
            }, f, indent=2)


# Global logger instance
logger = AgentLogger()