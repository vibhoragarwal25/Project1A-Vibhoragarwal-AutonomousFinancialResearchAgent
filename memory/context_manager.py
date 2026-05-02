# memory/context_manager.py

from agent.llm import llm_client

class ContextManager:
    """
    Manages short-term memory during a research session.
    
    Problem: A long research session generates more text
    than the LLM can hold in its context window.
    
    Solution: When context gets too long, summarize
    earlier steps while keeping key findings.
    
    Think of it like taking notes — you don't write
    every word, you capture key points.
    """
    
    # Claude Sonnet 4 has 200K tokens
    # Groq Llama has ~8K tokens
    # We use 6000 as safe limit for Groq
    MAX_CONTEXT_TOKENS = 6000
    SUMMARIZE_THRESHOLD = 4000
    
    def __init__(self):
        self.current_context = ""
        self.summarized_history = ""
        self.key_findings = []
        print("[Context] Context manager initialized")
    
    def add_to_context(self, text: str):
        """Add new information to current context"""
        self.current_context += f"\n{text}"
        
        # Check if we need to summarize
        estimated_tokens = len(self.current_context.split()) * 1.3
        
        if estimated_tokens > self.SUMMARIZE_THRESHOLD:
            print("[Context] Approaching context limit — summarizing...")
            self._summarize_and_compress()
    
    def _summarize_and_compress(self):
        """
        Compress older context while preserving key findings.
        This is how the agent handles long research sessions.
        """
        summary = llm_client.chat(
            system_prompt="""You are a research note-taker.
            Compress the following research session into 
            key bullet points. Preserve:
            - All numerical data with sources
            - Company names and dates
            - Risk factors identified
            - Conflicts between sources
            Discard: redundant observations, 
            failed tool attempts""",
            user_message=f"Compress this:\n{self.current_context}",
            max_tokens=500
        )
        
        self.summarized_history += f"\n[SUMMARIZED]: {summary}"
        
        # Keep only recent context
        lines = self.current_context.split('\n')
        self.current_context = '\n'.join(lines[-20:])
        
        print("[Context] Context compressed successfully")
    
    def get_full_context(self) -> str:
        """Get complete context including summaries"""
        if self.summarized_history:
            return f"""PREVIOUS RESEARCH SUMMARY:
{self.summarized_history}

RECENT CONTEXT:
{self.current_context}"""
        return self.current_context
    
    def add_key_finding(self, finding: str, source: str):
        """
        Record important findings separately.
        These are never compressed — always available.
        """
        self.key_findings.append({
            "finding": finding,
            "source": source
        })
        print(f"[Context] Key finding added: {finding[:60]}...")
    
    def get_key_findings(self) -> list:
        """Get all key findings from this session"""
        return self.key_findings
    
    def get_findings_summary(self) -> str:
        """Format key findings as readable text"""
        if not self.key_findings:
            return "No key findings recorded yet"
        
        return "\n".join([
            f"- {f['finding']} (Source: {f['source']})"
            for f in self.key_findings
        ])
    
    def reset(self):
        """Reset for new research session"""
        self.current_context = ""
        self.summarized_history = ""
        self.key_findings = []
        print("[Context] Context reset for new session")
    
    def get_stats(self) -> dict:
        """Context usage statistics"""
        total_words = len(self.current_context.split())
        estimated_tokens = int(total_words * 1.3)
        
        return {
            "current_context_words": total_words,
            "estimated_tokens": estimated_tokens,
            "token_limit": self.MAX_CONTEXT_TOKENS,
            "usage_percent": round(
                (estimated_tokens / self.MAX_CONTEXT_TOKENS) * 100, 1
            ),
            "key_findings_count": len(self.key_findings),
            "has_summarized_history": bool(self.summarized_history)
        }