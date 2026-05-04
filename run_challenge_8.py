import os
import time
from datetime import datetime
from agent.core import ARA1Agent
from tools.failure_injector import FailureInjectedRegistry
from tools import registry as real_registry

def run_challenge_8():
    print("=" * 60)
    print("CHALLENGE 8: Full Research Report With Degradation")
    print("Simulating 50% failure on financial_data_api + sec_filing_search")
    print("=" * 60)

    agent = ARA1Agent()
    agent.registry = FailureInjectedRegistry(
        real_registry=real_registry,
        failure_rate=0.5,
        affected_tools=["financial_data_api", "sec_filing_search"]
    )

    query = (
        "Produce a complete investment research report on NVIDIA Corporation. "
        "Note: The financial data API and SEC filing search tools are currently "
        "experiencing intermittent failures (simulate 50% failure rate)."
    )

    start = time.time()
    report = agent.research(query, urgency="standard")
    duration = round(time.time() - start, 2)

    injection_summary = agent.registry.get_injection_summary()

    os.makedirs("results", exist_ok=True)
    with open("results/challenge_8.md", "w") as f:
        f.write("# Challenge 8: Full Research Report With Degradation\n\n")
        f.write(f"**Duration:** {duration}s\n\n")
        f.write(f"**Injected Failures:** {injection_summary}\n\n")
        f.write("---\n\n")
        f.write(report)

    print(f"\n✅ Done in {duration}s")
    print(f"Injected failures: {injection_summary}")
    print("Saved to results/challenge_8.md")

if __name__ == "__main__":
    run_challenge_8()
