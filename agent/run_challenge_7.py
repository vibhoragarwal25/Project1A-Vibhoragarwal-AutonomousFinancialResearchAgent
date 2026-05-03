# run_challenge_7.py
# Place this in the ROOT of your project directory:
# Project1A-[YourName]-AutonomousFinancialResearchAgent/run_challenge_7.py

import os
from agent.core import agent

def run_challenge_7():
    query = """Based on the companies you've already researched,
what themes emerge across the technology sector?
Identify cross-cutting risks and opportunities."""

    print("=" * 60)
    print("CHALLENGE 7: Sector Analysis With Memory")
    print("=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    report = agent.research(query, urgency="standard")

    # Make sure results folder exists
    os.makedirs("results", exist_ok=True)

    output_path = "results/challenge_7.md"
    with open(output_path, "w") as f:
        f.write("# Challenge 7: Sector Analysis With Memory\n\n")
        f.write(f"**Query:** {query}\n\n")
        f.write("---\n\n")
        f.write(report)

    print(f"\n✅ Challenge 7 complete. Report saved to {output_path}")
    return report


if __name__ == "__main__":
    run_challenge_7()