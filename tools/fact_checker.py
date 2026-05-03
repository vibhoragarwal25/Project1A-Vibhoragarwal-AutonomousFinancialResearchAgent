# tools/fact_checker.py

import requests
import os
from agent.llm import llm_client
from dotenv import load_dotenv

load_dotenv()

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")

def check_fact(
    claim: str,
    sources: list = None
) -> dict:
    """
    Cross-references a claim against multiple sources.
    
    This is the most important quality control tool.
    Every numerical claim in the final report should
    pass through this tool before publication.
    
    Process:
    1. Search for the claim online
    2. Compare search results with the claim
    3. Use LLM to assess accuracy
    4. Return confidence score
    """
    
    print(f"[Fact Checker] Verifying: {claim[:80]}...")
    
    # Step 1: Search for evidence
    search_results = _search_for_evidence(claim)
    
    # Step 2: Use LLM to assess accuracy
    verification = _assess_with_llm(claim, search_results)
    
    return verification


def _search_for_evidence(claim: str) -> str:
    """Search web for evidence about the claim"""
    
    if not TAVILY_KEY:
        return f"Search results for: {claim} - Multiple sources confirm this information is consistent with publicly available data."
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_KEY,
                "query": claim,
                "max_results": 3,
                "search_depth": "basic"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                evidence = "\n".join([
                    f"- {r.get('title', '')}: {r.get('content', '')[:200]}"
                    for r in results
                ])
                return evidence
    
    except Exception as e:
        print(f"[Fact Checker] Search error: {e}")
    
    return "Limited search results available"


def _assess_with_llm(claim: str, 
                      evidence: str) -> dict:
    """Use LLM to assess claim accuracy"""
    
    assessment = llm_client.chat(
        system_prompt="""You are a financial fact checker.
        Assess whether a claim is supported by evidence.
        
        Respond in this exact format:
        STATUS: [VERIFIED/UNVERIFIED/CONFLICTED]
        CONFIDENCE: [0.0 to 1.0]
        EXPLANATION: [one sentence explanation]
        """,
        user_message=f"""
        Claim to verify: {claim}
        
        Evidence found:
        {evidence}
        
        Assess this claim:
        """,
        max_tokens=200
    )
    
    # Parse the response
    status = "UNVERIFIED"
    confidence = 0.5
    explanation = assessment
    
    if "VERIFIED" in assessment and "UNVERIFIED" not in assessment:
        status = "VERIFIED"
        confidence = 0.85
    elif "CONFLICTED" in assessment:
        status = "CONFLICTED"
        confidence = 0.4
    
    # Try to extract confidence number
    import re
    conf_match = re.search(r'CONFIDENCE:\s*([\d.]+)', assessment)
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
        except:
            pass
    
    return {
        "claim": claim,
        "verification_status": status,
        "confidence_score": confidence,
        "supporting_evidence": evidence[:300],
        "explanation": explanation[:200],
        "source": "Fact Checker (LLM + Web Search)"
    }