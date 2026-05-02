# agent/parser.py

import re
from typing import Optional

class AgentResponseParser:
    """
    Parses LLM responses into structured agent actions.
    The LLM returns text — this converts it into 
    tool calls the agent can execute.
    """
    
    def parse(self, response: str) -> dict:
        """
        Parse LLM response and extract:
        - thought: the reasoning
        - action: tool to call
        - params: tool parameters
        - final_answer: if research is complete
        """
        
        response = response.strip()
        
        # Check if agent is done
        if "FINAL_ANSWER:" in response:
            answer = response.split("FINAL_ANSWER:")[-1].strip()
            return {
                "type": "final_answer",
                "content": answer
            }
        
        # Extract thought
        thought = ""
        if "THOUGHT:" in response:
            thought_match = re.search(
                r'THOUGHT:\s*(.*?)(?=ACTION:|FINAL_ANSWER:|$)',
                response, 
                re.DOTALL
            )
            if thought_match:
                thought = thought_match.group(1).strip()
        
        # Extract action
        action = ""
        if "ACTION:" in response:
            action_match = re.search(
                r'ACTION:\s*(\w+)',
                response
            )
            if action_match:
                action = action_match.group(1).strip()
        
        # Extract params
        params = {}
        if "PARAMS:" in response:
            params_match = re.search(
                r'PARAMS:\s*(.*?)(?=THOUGHT:|ACTION:|FINAL_ANSWER:|$)',
                response,
                re.DOTALL
            )
            if params_match:
                params_str = params_match.group(1).strip()
                params = self._parse_params(params_str)
        
        # Determine response type
        if action:
            return {
                "type": "action",
                "thought": thought,
                "action": action,
                "params": params
            }
        elif thought:
            return {
                "type": "thought",
                "thought": thought
            }
        else:
            return {
                "type": "unknown",
                "raw": response
            }
    
    def _parse_params(self, params_str: str) -> dict:
        """
        Parse parameter string into dictionary.
        Handles formats like:
        ticker=AAPL, filing_type=10-K
        ticker=AAPL
        query=Apple revenue growth
        """
        params = {}
        
        # Try key=value format
        lines = params_str.replace(',', '\n').split('\n')
        for line in lines:
            line = line.strip()
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key:
                    params[key] = value
        
        return params
    
    def is_complete(self, response: str) -> bool:
        """Check if agent has finished research"""
        return "FINAL_ANSWER:" in response


# Global parser instance
parser = AgentResponseParser()