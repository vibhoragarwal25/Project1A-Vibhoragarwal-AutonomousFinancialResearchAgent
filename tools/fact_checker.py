# tools/fact_checker.py
def check_fact(claim: str, sources: list = None) -> dict:
    return {
        "claim": claim,
        "verification_status": "unverified",
        "confidence_score": 0.5,
        "supporting_evidence": [],
        "note": "Fact checker stub — real verification pending"
    }
