# agent/llm.py

import os
import time
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.max_retries = 5
        print(f"[LLM] Groq initialized")
    
    def chat(self,
             system_prompt: str,
             user_message: str,
             max_tokens: int = 2000) -> str:
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                )
                return response.choices[0].message.content
                
            except Exception as e:
                error = str(e).lower()
                
                if "rate_limit" in error or "429" in error:
                    delay = (2 ** attempt) + random.uniform(0, 0.5)
                    print(f"[LLM] Rate limited. Waiting {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                
                if "401" in error or "invalid" in error:
                    print("[LLM] Auth error — check GROQ_API_KEY")
                    return "LLM Error: Invalid API key"
                
                print(f"[LLM] Error attempt {attempt+1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return "LLM Error: Max retries exceeded"
    
    def test_connection(self) -> bool:
        print("[LLM] Testing Groq...")
        result = self.chat(
            "You are helpful.",
            "Say exactly: CONNECTION_SUCCESSFUL",
            50
        )
        if "CONNECTION_SUCCESSFUL" in result:
            print("[LLM] ✅ Connected")
            return True
        print(f"[LLM] ❌ Failed: {result}")
        return False
    
    def get_provider_status(self) -> dict:
        return {"provider": "groq", "model": self.model}
    
    def research_query(self, query: str, context: str = "") -> str:
        system = "You are ARA-1, a financial research analyst."
        if context:
            message = f"Query: {query}\n\nData:\n{context}"
        else:
            message = query
        return self.chat(system, message)


llm_client = LLMClient()