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
from memory.context_manager import ContextManager
from memory.episodic import EpisodicMemory
from dotenv import load_dotenv
from agent.error_handler import error_handler
from agent.circuit_breaker import circuit_breaker
from agent.fallback_chains import get_fallbacks
from agent.query_analyzer import query_analyzer
from agent.disambiguation import disambiguation_engine, detect_rate_of_change
load_dotenv()


class ARA1Agent:
    """
    ARA-1: Autonomous Research Agent
    Enhanced with full three-layer memory system.
    """

    def __init__(self):
        self.llm = llm_client
        self.registry = registry
        self.vector_store = VectorStore()
        self.context_manager = ContextManager()
        self.episodic_memory = EpisodicMemory()
        self.max_iterations = int(
            os.getenv("MAX_TOOL_CALLS", 20)
        )
        print("[ARA-1] Agent initialized with full memory system")

    def research(self, query: str, urgency: str = "standard") -> str:
        """
        Main research entry point.
        Uses disambiguation, edge-case detection, and all three memory layers.
        """

        # ── Step 0: Disambiguate query ────────────────────────────────────
        disambiguation = disambiguation_engine.process(query)

        if not disambiguation["should_proceed"]:
            questions = "\n".join(
                f"  • {q}" for q in disambiguation["questions"]
            )
            return (
                f"⚠️ Query is too ambiguous to proceed safely.\n\n"
                f"Please clarify:\n{questions}"
            )

        # Use refined query going forward
        refined_query = disambiguation["refined_query"]
        assumptions   = disambiguation["assumptions"]
        urgency       = disambiguation.get("urgency", urgency)

        if assumptions:
            print(f"\n[ARA-1] Proceeding with assumptions:")
            for a in assumptions:
                print(f"  → {a}")

        # ── Edge case check ───────────────────────────────────────────────
        analysis     = disambiguation["analysis"]
        edge_warning = disambiguation_engine.handle_edge_cases(query, analysis)
        if edge_warning:
            print(f"\n[ARA-1] {edge_warning}")

        # ── Reset context for new session ─────────────────────────────────
        self.context_manager.reset()
        self.logger = AgentLogger()

        self.logger.log_thought(
            f"New research query: {refined_query}"
        )

        print(f"\n{'='*60}")
        print(f"ARA-1 RESEARCH SESSION STARTED")
        print(f"Query: {refined_query}")
        print(f"Urgency: {urgency}")
        print(f"{'='*60}\n")

        # Detect query type for episodic memory
        query_type = self._detect_query_type(refined_query)

        # Step 1: Check episodic memory for lessons
        lessons = self.episodic_memory.get_lessons_for_query_type(
            query_type
        )
        if lessons:
            print(f"[ARA-1] Applying {len(lessons)} lessons from past research")
            for lesson in lessons:
                print(f"  → {lesson[:80]}")

        # Step 2: Check long-term memory
        memory_context = self._check_memory(refined_query)

        # Step 3: Create research plan
        plan = self._create_plan(refined_query, memory_context, lessons)

        # Step 4: Execute research
        gathered_data = self._execute_research(
            refined_query, plan, urgency
        )

        # ── Step 4b: Rate-of-change detection ────────────────────────────
        roc_warnings = detect_rate_of_change(gathered_data)
        if roc_warnings:
            print(f"\n[ARA-1] Temporal sensitivity flags detected:")
            for w in roc_warnings:
                print(f"  {w}")
            gathered_data += "\n\n## TEMPORAL SENSITIVITY FLAGS\n"
            gathered_data += "\n".join(roc_warnings)

        # Step 5: Synthesize
        report = self._synthesize(refined_query, gathered_data)

        # Step 6: Store findings
        self._store_findings(refined_query, report, query_type)

        # Step 7: Record episode
        self._record_episode(query_type, report)

        # Summary
        summary = self.logger.get_session_summary()
        print(f"\n{'='*60}")
        print(f"RESEARCH COMPLETE")
        print(f"Tool calls: {summary['tool_calls']}")
        print(f"Errors: {summary['errors']}")
        print(f"Key findings: {len(self.context_manager.get_key_findings())}")
        print(f"{'='*60}\n")

        return report

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _detect_query_type(self, query: str) -> str:
        """Classify query type for episodic memory lookup."""
        query_lower = query.lower()

        if any(word in query_lower for word in
               ["earnings", "quarterly", "revenue", "profit"]):
            return "earnings_analysis"

        elif any(word in query_lower for word in
                 ["risk", "threat", "challenge", "danger"]):
            return "risk_assessment"

        elif any(word in query_lower for word in
                 ["compare", "versus", "vs", "competitive"]):
            return "comparison"

        elif any(word in query_lower for word in
                 ["sector", "industry", "theme", "trend"]):
            return "sector_analysis"

        else:
            return "company_profile"

    def _check_memory(self, query: str) -> str:
        """Check long-term vector memory."""
        self.logger.log_thought(
            "Checking long-term memory for relevant past research"
        )

        results = self.vector_store.search(query, top_k=3)

        if results:
            memory_text = "\n".join([
                f"- {r['content'][:200]} "
                f"(Confidence: {r['metadata'].get('confidence', 'N/A')})"
                for r in results
            ])
            self.logger.log_thought(
                f"Found {len(results)} relevant memories"
            )
            return memory_text

        self.logger.log_thought("No relevant memories found")
        return ""

    def _create_plan(self, query: str,
                     memory_context: str,
                     lessons: list = None) -> str:
        """Create research plan using episodic lessons."""

        lessons_text = ""
        if lessons:
            lessons_text = "\nLessons from past similar research:\n"
            lessons_text += "\n".join(
                f"- {l}" for l in lessons
            )

        planning_prompt = get_planning_prompt(
            query,
            memory_context + lessons_text
        )

        plan = self.llm.chat(
            system_prompt="""You are ARA-1 research planner. 
            Create efficient research plans using past lessons.""",
            user_message=planning_prompt,
            max_tokens=800
        )

        print(f"\n📋 RESEARCH PLAN:\n{plan}\n")
        self.logger.log_thought(f"Plan created")
        self.context_manager.add_to_context(
            f"Research Plan:\n{plan}"
        )

        return plan

    def _execute_research(self, query: str,
                          plan: str,
                          urgency: str) -> str:
        """Execute ReAct loop with context management."""

        tools_list = self.registry.get_tools_for_llm()
        tools_description = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in tools_list
        ])

        system_prompt = get_system_prompt(tools_description)

        iteration_count = 0
        gathered_data   = []
        tool_results    = {}

        max_calls = {
            "critical": 5,
            "urgent":   10,
            "standard": self.max_iterations
        }.get(urgency, self.max_iterations)

        conversation = f"""Research Query: {query}

Research Plan:
{plan}

Begin research now using THOUGHT/ACTION/PARAMS format."""

        while iteration_count < max_calls:
            iteration_count += 1
            print(f"\n--- Iteration {iteration_count}/{max_calls} ---")

            # Use context manager for long sessions
            full_context = self.context_manager.get_full_context()
            if full_context:
                current_message = (
                    f"{conversation}\n\nContext so far:\n"
                    f"{full_context[-2000:]}"
                )
            else:
                current_message = conversation

            response = self.llm.chat(
                system_prompt=system_prompt,
                user_message=current_message,
                max_tokens=2000
            )

            parsed = parser.parse(response)

            if parsed["type"] == "final_answer":
                self.logger.log_thought("Research complete")
                gathered_data.append(parsed["content"])
                break

            elif parsed["type"] == "action":
                thought = parsed.get("thought", "")
                action  = parsed.get("action", "")
                params  = parsed.get("params", {})

                if thought:
                    self.logger.log_thought(thought)
                    self.context_manager.add_to_context(
                        f"Thought: {thought}"
                    )

                if action:
                    self.logger.log_action(action, params)

                    # Check circuit breaker first
                    if not circuit_breaker.is_available(action):
                        print(f"[ARA-1] Circuit open for {action}, skipping")
                        observation = (
                            f"Tool {action} circuit is open due to repeated "
                            f"failures. Using alternative approach."
                        )
                        conversation += (
                            f"\n\nASSISTANT: {response}"
                            f"\n\nOBSERVATION: {observation}\n\nContinue:"
                        )
                        continue

                    # Try to execute with error handling
                    try:
                        result  = self.registry.execute(action, params)
                        success = result.get("success", False)

                        if success:
                            circuit_breaker.record_success(action)
                        else:
                            circuit_breaker.record_failure(action)

                            # Try fallback chain
                            fallbacks = get_fallbacks(action)
                            if fallbacks:
                                print(
                                    f"[ARA-1] Primary tool failed, "
                                    f"trying fallbacks: {fallbacks}"
                                )
                                fallback_result = error_handler.handle_tool_error(
                                    tool_name=action,
                                    error=Exception(
                                        result.get("error", "Unknown")
                                    ),
                                    fallback_chain=fallbacks,
                                    params=params,
                                    registry=self.registry
                                )
                                if fallback_result.get("success"):
                                    result  = fallback_result
                                    success = True
                                    circuit_breaker.record_success(
                                        fallback_result.get(
                                            "fallback_tool", action
                                        )
                                    )

                    except Exception as e:
                        circuit_breaker.record_failure(action)
                        self.logger.log_error(action, str(e))

                        # Try fallback chain
                        fallbacks = get_fallbacks(action)
                        result  = error_handler.handle_tool_error(
                            tool_name=action,
                            error=e,
                            fallback_chain=fallbacks,
                            params=params,
                            registry=self.registry
                        )
                        success = result.get("success", False)

                    self.logger.log_observation(action, result, success)

                    # Track tool performance
                    if action not in tool_results:
                        tool_results[action] = []
                    tool_results[action].append(success)

                    if success:
                        data     = result.get("data", {})
                        data_str = str(data)[:500]
                        gathered_data.append(f"[{action}]: {data_str}")

                        self.context_manager.add_key_finding(
                            finding=data_str[:100],
                            source=action
                        )

                        # Add fallback note if used
                        if result.get("fallback_used"):
                            from agent.fallback_chains import get_confidence_note
                            note = get_confidence_note(
                                result.get("original_tool", action),
                                result.get("fallback_tool", action)
                            )
                            gathered_data.append(note)

                        observation = (
                            f"Tool {action} returned: {data_str[:300]}"
                        )
                        self.context_manager.add_to_context(
                            f"Observation: {observation}"
                        )

                    else:
                        error            = result.get("error", "Unknown")
                        degradation_note = result.get("report_note", "")
                        self.logger.log_error(action, error)

                        if degradation_note:
                            gathered_data.append(
                                f"[DATA GAP — {action}]: {degradation_note}"
                            )

                        observation = (
                            f"Tool {action} unavailable: {error}. "
                            f"{degradation_note}"
                        )

                    conversation += (
                        f"\n\nASSISTANT: {response}"
                        f"\n\nOBSERVATION: {observation}\n\nContinue:"
                    )

                else:
                    thought = parsed.get("thought", response)
                    self.logger.log_thought(thought)
                    conversation += (
                        f"\n\nASSISTANT: {response}\n\nContinue:"
                    )

        # Calculate tool efficiency for episodic memory
        self.tool_results = tool_results

        return "\n\n".join(gathered_data)

    def _synthesize(self, query: str,
                    gathered_data: str) -> str:
        """Synthesize with key findings from context."""

        key_findings = self.context_manager.get_findings_summary()

        enhanced_data = f"""
GATHERED DATA:
{gathered_data}

KEY FINDINGS EXTRACTED:
{key_findings}
"""

        synthesis_prompt = get_synthesis_prompt(query, enhanced_data)

        report = self.llm.chat(
            system_prompt="""You are ARA-1 synthesis engine.
            Produce professional investment research reports.
            Never fabricate data. Always cite sources.
            Include source reliability notes.""",
            user_message=synthesis_prompt,
            max_tokens=4000
        )

        return report

    def _store_findings(self, query: str,
                        report: str,
                        query_type: str):
        """Store findings in long-term vector memory."""

        common_tickers = [
            "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN",
            "NVDA", "META", "NFLX", "JPM", "GS", "PLTR"
        ]

        ticker = "GENERAL"
        for t in common_tickers:
            if t in query.upper():
                ticker = t
                break

        # Store full report summary
        self.vector_store.store(
            content=report[:800],
            ticker=ticker,
            source_type=query_type,
            confidence=0.8
        )

        # Store key findings separately for better retrieval
        for finding in self.context_manager.get_key_findings():
            self.vector_store.store(
                content=finding["finding"],
                ticker=ticker,
                source_type=finding["source"],
                confidence=0.9
            )

        stored_count = 1 + len(self.context_manager.get_key_findings())
        print(f"[ARA-1] Stored {stored_count} records to memory")

    def _record_episode(self, query_type: str, report: str):
        """Record this session in episodic memory."""

        # Calculate tool success rates
        tool_success_rates = {}
        if hasattr(self, 'tool_results'):
            for tool, results in self.tool_results.items():
                if results:
                    tool_success_rates[tool] = sum(results) / len(results)

        # Simple quality estimate based on report length
        quality_score = min(0.9, len(report.split()) / 500)

        # Generate lesson
        tools_that_worked = [
            t for t, r in tool_success_rates.items() if r > 0.5
        ]

        lesson = (
            f"For {query_type}: tools {tools_that_worked} performed well. "
            f"Report quality: {quality_score:.2f}"
        )

        self.episodic_memory.record_episode(
            query_type=query_type,
            tools_used=list(tool_success_rates.keys()),
            tool_success_rates=tool_success_rates,
            quality_score=quality_score,
            key_lesson=lesson
        )


# Global agent instance
agent = ARA1Agent()