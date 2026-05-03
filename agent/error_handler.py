# agent/error_handler.py

import time
import random
import functools
from datetime import datetime
from typing import Callable, Any

class ErrorHandler:
    """
    Handles all errors in ARA-1 with three strategies:
    
    1. Retry with exponential backoff
       For temporary failures (rate limits, timeouts)
       
    2. Fallback to alternative tool
       When primary tool is unavailable
       
    3. Graceful degradation
       When all options exhausted — report gap transparently
    
    This is what separates a production system from a demo.
    """
    
    def __init__(self):
        self.error_log = []
        self.recovery_log = []
        
        # Exponential backoff config from spec
        self.initial_delay = 1.0
        self.backoff_multiplier = 2.0
        self.max_retries = 5
        self.jitter_range = 0.5
        self.max_delay = 32.0
        
        print("[ErrorHandler] Initialized")
    
    def with_retry(self, 
                   func: Callable,
                   *args,
                   **kwargs) -> Any:
        """
        Execute a function with exponential backoff retry.
        
        Delay sequence:
        Attempt 1: 1.0s + random(0, 0.5)
        Attempt 2: 2.0s + random(0, 0.5)
        Attempt 3: 4.0s + random(0, 0.5)
        Attempt 4: 8.0s + random(0, 0.5)
        Attempt 5: 16.0s + random(0, 0.5)
        """
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    # Recovered from error
                    self.recovery_log.append({
                        "function": func.__name__,
                        "attempts_needed": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"[ErrorHandler] ✅ Recovered after {attempt + 1} attempts")
                
                return result
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Log the error
                self.error_log.append({
                    "function": func.__name__,
                    "attempt": attempt + 1,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Don't retry auth errors — they won't fix themselves
                if any(word in error_str for word in 
                       ["401", "403", "invalid key", 
                        "unauthorized", "authentication"]):
                    print(f"[ErrorHandler] Auth error — not retrying: {e}")
                    break
                
                # Don't retry not found errors
                if "404" in error_str:
                    print(f"[ErrorHandler] Not found — not retrying: {e}")
                    break
                
                # Calculate delay with exponential backoff + jitter
                delay = min(
                    self.initial_delay * (self.backoff_multiplier ** attempt),
                    self.max_delay
                )
                jitter = random.uniform(0, self.jitter_range)
                total_delay = delay + jitter
                
                print(f"[ErrorHandler] Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    print(f"[ErrorHandler] Retrying in {total_delay:.1f}s...")
                    time.sleep(total_delay)
        
        print(f"[ErrorHandler] All {self.max_retries} attempts failed")
        raise last_error
    
    def handle_tool_error(self,
                           tool_name: str,
                           error: Exception,
                           fallback_chain: list,
                           params: dict,
                           registry) -> dict:
        """
        Handle a tool failure by trying fallback chain.
        
        fallback_chain: ordered list of fallback tool names
        Returns result from first successful fallback,
        or graceful degradation response if all fail.
        """
        
        print(f"[ErrorHandler] Tool failed: {tool_name}")
        print(f"[ErrorHandler] Trying fallback chain: {fallback_chain}")
        
        self.error_log.append({
            "tool": tool_name,
            "error": str(error),
            "fallbacks_available": fallback_chain,
            "timestamp": datetime.now().isoformat()
        })
        
        # Try each fallback
        for fallback_name in fallback_chain:
            print(f"[ErrorHandler] Trying fallback: {fallback_name}")
            
            try:
                result = registry.execute(fallback_name, params)
                
                if result.get("success"):
                    self.recovery_log.append({
                        "original_tool": tool_name,
                        "fallback_used": fallback_name,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    print(f"[ErrorHandler] ✅ Fallback {fallback_name} succeeded")
                    
                    # Add note that fallback was used
                    result["fallback_used"] = True
                    result["original_tool"] = tool_name
                    result["fallback_tool"] = fallback_name
                    result["confidence_note"] = f"Data from fallback source {fallback_name} — may be less precise than {tool_name}"
                    
                    return result
                    
            except Exception as fe:
                print(f"[ErrorHandler] Fallback {fallback_name} also failed: {fe}")
                continue
        
        # All fallbacks failed — graceful degradation
        print(f"[ErrorHandler] All fallbacks exhausted for {tool_name}")
        
        return self._graceful_degradation(
            tool_name, fallback_chain, str(error)
        )
    
    def _graceful_degradation(self,
                               tool_name: str,
                               fallbacks_tried: list,
                               original_error: str) -> dict:
        """
        When all options fail, return transparent response.
        Never fabricate data. Always explain the gap.
        """
        
        return {
            "success": False,
            "graceful_degradation": True,
            "tool": tool_name,
            "fallbacks_tried": fallbacks_tried,
            "error": original_error,
            "report_note": f"Data from {tool_name} unavailable. Fallbacks {fallbacks_tried} also failed. This section of the report may be incomplete. Recommend manual verification.",
            "data": None
        }
    
    def get_error_summary(self) -> dict:
        """
        Summary of all errors and recoveries.
        Used for evaluation metrics AB-2 (Error Recovery Rate).
        """
        total_errors = len(self.error_log)
        total_recoveries = len(self.recovery_log)
        
        recovery_rate = (
            total_recoveries / total_errors * 100
            if total_errors > 0 else 100.0
        )
        
        return {
            "total_errors": total_errors,
            "successful_recoveries": total_recoveries,
            "recovery_rate_pct": round(recovery_rate, 1),
            "target_recovery_rate": 90.0,
            "meets_target": recovery_rate >= 90.0,
            "error_log": self.error_log[-5:],
            "recovery_log": self.recovery_log[-5:]
        }
    
    def inject_failure(self, 
                       failure_rate: float = 0.5) -> bool:
        """
        Simulate random tool failures for stress testing.
        Used in Challenge 8 (50% failure rate simulation).
        
        failure_rate: 0.5 = 50% of calls will fail
        """
        return random.random() < failure_rate


# Global instance
error_handler = ErrorHandler()