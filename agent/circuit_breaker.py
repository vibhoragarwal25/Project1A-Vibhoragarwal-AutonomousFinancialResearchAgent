# agent/circuit_breaker.py

import time
from datetime import datetime
from typing import Dict

class CircuitBreaker:
    """
    Prevents cascading failures when multiple tools fail.
    
    How it works:
    - CLOSED: Tool is working normally
    - OPEN: Tool failed too many times, skip it
    - HALF_OPEN: Testing if tool has recovered
    
    If a tool fails 3+ times in one session,
    circuit opens and that tool is bypassed.
    This prevents wasting retry budget on a broken tool.
    
    Real example:
    SEC EDGAR goes down for maintenance.
    Without circuit breaker: Agent retries 5 times
    for every single SEC call = 50 wasted retries.
    With circuit breaker: After 3 failures, open circuit.
    Agent immediately uses fallback for remaining calls.
    """
    
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Tool bypassed
    HALF_OPEN = "HALF_OPEN"  # Testing recovery
    
    def __init__(self,
                 failure_threshold: int = 3,
                 recovery_timeout: int = 60):
        """
        failure_threshold: failures before opening circuit
        recovery_timeout: seconds before testing recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        # Track state per tool
        self.circuits: Dict[str, dict] = {}
        
        print(f"[CircuitBreaker] Initialized")
        print(f"  Threshold: {failure_threshold} failures")
        print(f"  Recovery timeout: {recovery_timeout}s")
    
    def _get_circuit(self, tool_name: str) -> dict:
        """Get or create circuit state for a tool"""
        if tool_name not in self.circuits:
            self.circuits[tool_name] = {
                "state": self.CLOSED,
                "failure_count": 0,
                "last_failure_time": None,
                "last_state_change": datetime.now().isoformat()
            }
        return self.circuits[tool_name]
    
    def is_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available to call.
        Returns False if circuit is OPEN.
        """
        circuit = self._get_circuit(tool_name)
        
        if circuit["state"] == self.CLOSED:
            return True
        
        elif circuit["state"] == self.OPEN:
            # Check if recovery timeout has passed
            if circuit["last_failure_time"]:
                elapsed = time.time() - circuit["last_failure_time"]
                
                if elapsed >= self.recovery_timeout:
                    # Move to half-open to test recovery
                    circuit["state"] = self.HALF_OPEN
                    print(f"[CircuitBreaker] {tool_name}: OPEN → HALF_OPEN (testing recovery)")
                    return True
            
            print(f"[CircuitBreaker] {tool_name} circuit is OPEN — skipping")
            return False
        
        elif circuit["state"] == self.HALF_OPEN:
            # Allow one test call
            return True
        
        return True
    
    def record_success(self, tool_name: str):
        """Record a successful tool call"""
        circuit = self._get_circuit(tool_name)
        
        if circuit["state"] == self.HALF_OPEN:
            # Recovery confirmed — close circuit
            circuit["state"] = self.CLOSED
            circuit["failure_count"] = 0
            circuit["last_state_change"] = datetime.now().isoformat()
            print(f"[CircuitBreaker] {tool_name}: HALF_OPEN → CLOSED (recovered)")
        
        elif circuit["state"] == self.CLOSED:
            # Reset failure count on success
            circuit["failure_count"] = 0
    
    def record_failure(self, tool_name: str):
        """Record a failed tool call"""
        circuit = self._get_circuit(tool_name)
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = time.time()
        
        if circuit["state"] == self.HALF_OPEN:
            # Still failing after recovery period
            circuit["state"] = self.OPEN
            print(f"[CircuitBreaker] {tool_name}: HALF_OPEN → OPEN (still failing)")
        
        elif circuit["failure_count"] >= self.failure_threshold:
            # Too many failures — open the circuit
            circuit["state"] = self.OPEN
            circuit["last_state_change"] = datetime.now().isoformat()
            print(f"[CircuitBreaker] ⚡ {tool_name}: CLOSED → OPEN after {circuit['failure_count']} failures")
    
    def get_status(self) -> dict:
        """Get status of all circuits"""
        status = {}
        for tool, circuit in self.circuits.items():
            status[tool] = {
                "state": circuit["state"],
                "failure_count": circuit["failure_count"],
                "available": self.is_available(tool)
            }
        return status
    
    def reset_all(self):
        """Reset all circuits — use between research sessions"""
        self.circuits = {}
        print("[CircuitBreaker] All circuits reset")
    
    def get_open_circuits(self) -> list:
        """Get list of tools with open circuits"""
        return [
            tool for tool, circuit in self.circuits.items()
            if circuit["state"] == self.OPEN
        ]


# Global instance
circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=60
)