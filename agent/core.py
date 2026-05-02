# agent/core.py

import os
import sys
sys.path.append('..')

from agent.llm import llm_client
from agent.logger import AgentLogger
from agent.parser import parser
from agent.prompts import (
    get_system_prompt,
    get_planning_prompt,
    get_synthesis_prompt
)
from tools import registry
from memory.vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()

class ARA1Agent:
    """
    ARA-1: Autonomous Research Agent
    
    The core agent that orchestrates everything:
    - Receives research queries
    - Plans research approach
    - Executes tools
    - Synthesizes findings
    - Produces research reports
    """
    
    def __init__(self):
        self.llm = llm_client
        self.registry = registry
        self.vector_store = VectorStore()
        self.max_iterations = int(
            os.getenv("MAX_TOOL_CALLS", 20)
        )
        print("[ARA-1] Agent initialized and ready")
    
    def research(self, query: str, 
                 urgency: str = "standard") -> str:
        """
        Main entry point for research tasks.
        
        urgency levels:
        - critical: 30 min SLA, brief output
        - urgent: 1 hour SLA, moderate depth  
        - standard: 4 hour SLA, full depth
        
        Example:
        report = agent.research(
            "Analyze Apple Inc quarterly earnings"
        )
        """
        
        # Create session logger
        self.logger = AgentLogger()
        self.logger.log_thought(
            f"New research query received: {query}"
        )
        
        print(f"\n{'='*60}")
        print(f"ARA-1 RESEARCH SESSION STARTED")
        print(f"Query: {query}")
        print(f"Urgency: {urgency}")
        print(f"{'='*60}\n")
        
        # Step 1: Check long-term memory first
        memory_context = self._check_memory(query)
        
        # Step 2: Create research plan
        plan = self._create_plan(query, memory_context)
        
        # Step 3: Execute research loop
        gathered_data = self._execute_research(
            query, plan, urgency
        )
        
        # Step 4: Synthesize findings
        report = self._synthesize(query, gathered_data)
        
        # Step 5: Store findings in memory
        self._store_findings(query, report)
        
        # Step 6: Log session summary
        summary = self.logger.get_session_summary()
        print(f"\n{'='*60}")
        print(f"RESEARCH COMPLETE")
        print(f"Total steps: {summary['total_steps']}")
        print(f"Tool calls: {summary['tool_calls']}")
        print(f"Errors: {summary['errors']}")
        print(f"{'='*60}\n")
        
        return report
    
    def _check_memory(self, query: str) -> str:
        """
        Always check long-term memory first.
        Avoids repeating research already done.
        """
        self.logger.log_thought(
            "Checking long-term memory for relevant past research"
        )
        
        results = self.vector_store.search(query, top_k=3)
        
        if results:
            memory_text = "\n".join([
                f"- {r['content']} "
                f"(Source: {r['metadata'].get('source_type', 'unknown')}, "
                f"Confidence: {r['metadata'].get('confidence', 'unknown')})"
                for r in results
            ])
            self.logger.log_thought(
                f"Found {len(results)} relevant memories"
            )
            return memory_text
        
        self.logger.log_thought("No relevant memories found")
        return ""
    
    def _create_plan(self, query: str, 
                     memory_context: str) -> str:
        """
        Create a structured research plan.
        This is the Plan part of Plan-and-Execute.
        """
        self.logger.log_thought(
            "Creating research plan"
        )
        
        planning_prompt = get_planning_prompt(
            query, memory_context
        )
        
        plan = self.llm.chat(
            system_prompt="You are ARA-1 research planner. Create efficient, non-redundant research plans.",
            user_message=planning_prompt,
            max_tokens=1000
        )
        
        print(f"\n📋 RESEARCH PLAN:\n{plan}\n")
        self.logger.log_thought(f"Plan created: {plan}")
        
        return plan
    
    def _execute_research(self, query: str,
                          plan: str,
                          urgency: str) -> str:
        """
        Execute the ReAct loop to gather information.
        Thought → Action → Observation → repeat
        """
        
        # Build tools description for system prompt
        tools_list = self.registry.get_tools_for_llm()
        tools_description = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in tools_list
        ])
        
        system_prompt = get_system_prompt(tools_description)
        
        # Build initial message
        iteration_count = 0
        gathered_data = []
        
        # Adjust depth based on urgency
        max_calls = {
            "critical": 5,
            "urgent": 10,
            "standard": self.max_iterations
        }.get(urgency, self.max_iterations)
        
        conversation = f"""Research Query: {query}

Research Plan:
{plan}

Begin your research now. Follow the THOUGHT/ACTION/PARAMS 
format strictly."""
        
        while iteration_count < max_calls:
            iteration_count += 1
            print(f"\n--- Iteration {iteration_count} ---")
            
            # Get agent's next action
            response = self.llm.chat(
                system_prompt=system_prompt,
                user_message=conversation,
                max_tokens=2000
            )
            
            # Parse the response
            parsed = parser.parse(response)
            
            # Agent is done
            if parsed["type"] == "final_answer":
                self.logger.log_thought(
                    "Agent determined research is complete"
                )
                gathered_data.append(parsed["content"])
                break
            
            # Agent wants to use a tool
            elif parsed["type"] == "action":
                thought = parsed.get("thought", "")
                action = parsed.get("action", "")
                params = parsed.get("params", {})
                
                if thought:
                    self.logger.log_thought(thought)
                
                if action:
                    # Execute the tool
                    self.logger.log_action(action, params)
                    result = self.registry.execute(action, params)
                    
                    success = result.get("success", False)
                    self.logger.log_observation(
                        action, result, success
                    )
                    
                    if success:
                        data = result.get("data", {})
                        gathered_data.append(
                            f"[{action}]: {str(data)[:500]}"
                        )
                        observation = f"Tool {action} returned: {str(data)[:300]}"
                    else:
                        error = result.get("error", "Unknown error")
                        self.logger.log_error(action, error)
                        observation = f"Tool {action} failed: {error}. Try a different approach."
                    
                    # Add to conversation
                    conversation += f"\n\nASSISTANT: {response}\n\nOBSERVATION: {observation}\n\nContinue research:"
            
            # Just a thought, no action
            else:
                thought = parsed.get("thought", response)
                self.logger.log_thought(thought)
                conversation += f"\n\nASSISTANT: {response}\n\nContinue:"
        
        return "\n\n".join(gathered_data)
    
    def _synthesize(self, query: str, 
                    gathered_data: str) -> str:
        """
        Synthesize all gathered data into final report.
        This is where financial analysis happens.
        """
        self.logger.log_thought(
            "Synthesizing all gathered data into report"
        )
        
        synthesis_prompt = get_synthesis_prompt(
            query, gathered_data
        )
        
        report = self.llm.chat(
            system_prompt="""You are ARA-1 synthesis engine. 
            Produce professional investment research reports.
            Never fabricate data. Always cite sources.""",
            user_message=synthesis_prompt,
            max_tokens=4000
        )
        
        return report
    
    def _store_findings(self, query: str, report: str):
        """
        Store research findings in long-term memory.
        Next time a similar query comes in,
        agent can reuse these findings.
        """
        self.logger.log_thought(
            "Storing findings in long-term memory"
        )
        
        # Extract ticker from query if present
        common_tickers = [
            "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN",
            "NVDA", "META", "NFLX", "JPM", "GS"
        ]
        ticker = "GENERAL"
        for t in common_tickers:
            if t in query.upper():
                ticker = t
                break
        
        self.vector_store.store(
            content=report[:1000],
            ticker=ticker,
            source_type="agent_research",
            confidence=0.8
        )
        
        print(f"[ARA-1] Findings stored to memory")


# Global agent instance
agent = ARA1Agent()