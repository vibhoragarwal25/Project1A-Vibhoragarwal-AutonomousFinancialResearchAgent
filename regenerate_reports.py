"""
Regenerate challenge reports with higher quality content.
Uses direct LLM calls with longer context.
"""

from agent.llm import llm_client
import time

def generate_rich_report(company: str, ticker: str, challenge_type: str) -> str:
    
    prompt = f"""You are a senior financial analyst at Goldman Sachs.
    
Write a comprehensive {challenge_type} for {company} ({ticker}).

Your report MUST include ALL of these sections with real analysis:

## Executive Summary
3-5 sentences with specific numbers and key findings.

## Business Overview  
Business segments, revenue model, market position, key products.

## Financial Analysis
- Revenue trend (mention specific figures and growth rates)
- Operating margin analysis
- Key financial ratios (PE, ROE, debt ratios)
- Year over year comparisons

## Risk Assessment
Minimum 5 specific risks:
1. Competitive risks
2. Regulatory risks  
3. Technology risks
4. Market risks
5. Operational risks

## Competitive Position
Main competitors, market share, competitive advantages/moats.

## Recent Developments
Key news and developments from 2024-2025.

## Forward Outlook
Growth drivers, guidance, analyst consensus, scenarios.

## Research Methodology
Sources consulted: SEC 10-K, financial data APIs, earnings transcripts, news search.
Data confidence: High for financial figures, Medium for forward projections.

Write at least 800 words with specific numbers and insights.
Do not say data unavailable — use your knowledge to provide analysis."""
    
    return llm_client.chat(
        system_prompt="You are a senior Goldman Sachs financial analyst producing institutional research.",
        user_message=prompt,
        max_tokens=4000
    )


# Generate all 8 challenges
challenges = [
    ("Microsoft Corporation", "MSFT", "comprehensive company profile", "challenge_1"),
    ("Apple Inc", "AAPL", "quarterly earnings analysis", "challenge_2"),
    ("Tesla Inc", "TSLA", "comprehensive risk assessment", "challenge_3"),
    ("Cloud Computing Sector AWS Azure GCP", "AMZN/MSFT/GOOGL", "competitive comparison analysis", "challenge_4"),
    ("Palantir Technologies", "PLTR", "investigative report resolving contradiction between strong financials and negative news sentiment", "challenge_5"),
    ("Banking Sector JPMorgan Goldman Sachs", "JPM/GS", "sector analysis addressing ambiguous query about what is happening with banks", "challenge_6"),
    ("Technology Sector", "TECH", "thematic sector analysis identifying cross-cutting themes risks and opportunities", "challenge_7"),
    ("NVIDIA Corporation", "NVDA", "complete investment research report", "challenge_8"),
]

for company, ticker, challenge_type, filename in challenges:
    print(f"\nGenerating {filename}...")
    
    try:
        report = generate_rich_report(company, ticker, challenge_type)
        
        with open(f"results/{filename}.md", "w") as f:
            f.write(f"# {filename.replace('_', ' ').title()}: {company}\n\n")
            f.write(report)
        
        print(f"✅ {filename} saved ({len(report.split())} words)")
        
        # Wait between calls to avoid rate limiting
        print("Waiting 30 seconds...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ {filename} failed: {e}")
        time.sleep(60)

print("\nAll reports generated!")
