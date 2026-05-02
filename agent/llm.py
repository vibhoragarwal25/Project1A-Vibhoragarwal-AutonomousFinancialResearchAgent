# agent/llm.py

import os
from dotenv import load_dotenv
from groq import Groq
import time
import random

load_dotenv()

class LLMClient:
    """
    Handles all communication with Groq (free tier).
    Model: llama-3.3-70b-versatile
    """
    
    def __init__(self):
        self.provider = "groq"
        self.model = os.getenv(
            "LLM_MODEL", 
            "llama-3.3-70b-versatile"
        )
        self.max_retries = int(os.getenv("MAX_RETRIES", 5))
        
        # Initialize Groq client
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        print(f"[LLM] Initialized Groq client")
        print(f"[LLM] Model: {self.model}")
    
    def chat(self,
             system_prompt: str,
             user_message: str,
             max_tokens: int = 4000) -> str:
        """
        Send a message to Groq and get a response.
        This is the core thinking function of your agent.
        
        Example:
        response = llm_client.chat(
            system_prompt="You are a financial analyst",
            user_message="Analyze Apple's revenue growth"
        )
        """
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user", 
                            "content": user_message
                        }
                    ]
                )
                return response.choices[0].message.content
                
            except Exception as e:
                error_str = str(e)
                
                # Rate limit handling
                if "rate_limit" in error_str.lower() or "429" in error_str:
                    delay = (2 ** attempt) + random.uniform(0, 0.5)
                    print(f"[LLM] Rate limited. Waiting {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                
                # Auth error — no point retrying
                if "401" in error_str or "invalid" in error_str.lower():
                    print(f"[LLM] Authentication error — check your GROQ_API_KEY in .env")
                    return f"LLM Error: Invalid API key"
                
                # Other errors — retry with backoff
                print(f"[LLM] Error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return f"LLM Error: {str(e)}"
        
        return "LLM Error: Max retries exceeded"
    
    def test_connection(self) -> bool:
        """
        Test that your Groq API key works.
        Run this after setting up your key.
        """
        print(f"[LLM] Testing Groq connection...")
        
        response = self.chat(
            system_prompt="You are a helpful assistant.",
            user_message="Say exactly this word and nothing else: CONNECTION_SUCCESSFUL",
            max_tokens=50
        )
        
        if "CONNECTION_SUCCESSFUL" in response:
            print(f"[LLM] ✅ Groq connection successful!")
            print(f"[LLM] Response: {response}")
            return True
        else:
            print(f"[LLM] ❌ Unexpected response: {response}")
            return False
    
    def research_query(self, 
                       query: str,
                       context: str = "") -> str:
        """
        Specialized function for financial research queries.
        Used by the agent to analyze gathered data.
        """
        system_prompt = """You are ARA-1, an autonomous financial 
        research agent. You analyze financial data and produce 
        professional investment research reports.
        
        Rules:
        - Never fabricate data
        - Always cite sources
        - Flag uncertainty explicitly
        - Be precise with numbers
        - Think like a senior financial analyst"""
        
        if context:
            user_message = f"""
            Research Query: {query}
            
            Available Data:
            {context}
            
            Provide your analysis:
            """
        else:
            user_message = query
        
        return self.chat(system_prompt, user_message)


# Global instance used across the project
llm_client = LLMClient()