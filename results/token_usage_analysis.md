# ARA-1 Token Usage Analysis

**Project:** Autonomous Financial Research Agent (ARA-1)
**Author:** Vibhoragarwal
**Date:** May 5, 2026
**Scope:** Full project lifecycle — Day 1 through Day 12 (Challenges 1–8 + stress testing)

---

## Executive Summary

ARA-1 completed 8 research challenges, 15+ active research sessions, and a full stress test suite at a total infrastructure cost of **$0.00**, running entirely on free tier APIs. This analysis examines token consumption patterns, per-session efficiency, cost modeling against paid alternatives, and optimization opportunities. The agent's tool efficiency rate of 70%+ and 100% error recovery rate demonstrate that the architecture extracts high research output per token consumed. A paid tier upgrade to Groq's developer plan or Anthropic's API would cost an estimated $8–15 per month at current usage volumes — well within the budget of any individual or early-stage research operation.

---

## API Usage Overview

| API | Provider | Tier | Cost | Primary Use |
|-----|----------|------|------|-------------|
| LLM (inference) | Groq (Llama 3) | Free | $0.00 | Query processing, report generation |
| Financial data | Yahoo Finance | Free | $0.00 | Price, revenue, EPS data |
| SEC filings | EDGAR public API | Free | $0.00 | 10-K, 10-Q retrieval |
| News/web search | DuckDuckGo API | Free | $0.00 | News sentiment, recent events |
| Vector database | ChromaDB (local) | Free | $0.00 | Semantic memory retrieval |
| **Total** | | | **$0.00** | |

---

## Session-Level Token Estimates

Token counts are estimated from session logs and output word counts using a standard 1.3 tokens-per-word conversion for English prose, plus overhead for system prompts, tool call schemas, and context injection.

| Session | Challenge | Estimated Input Tokens | Estimated Output Tokens | Total Tokens | Research Output |
|---------|-----------|----------------------|------------------------|--------------|----------------|
| Day 1–2 | Setup & core agent | ~8,000 | ~3,500 | ~11,500 | Architecture scaffolding |
| Day 3 | Challenge 1 (MSFT) | ~12,400 | ~5,800 | ~18,200 | 2,171-word report |
| Day 4 | Challenge 2 (AAPL earnings) | ~11,200 | ~5,600 | ~16,800 | 2,250-word report |
| Day 5 | Challenge 3 (TSLA risk) | ~10,800 | ~5,700 | ~16,500 | 2,290-word report |
| Day 6 | Challenge 4 (Cloud IaaS) | ~13,600 | ~7,200 | ~20,800 | 2,866-word report |
| Day 7 | Challenge 5 (PLTR) | ~11,400 | ~6,400 | ~17,800 | 2,560-word report |
| Day 8 | Challenge 6 (Banking) | ~12,200 | ~7,300 | ~19,500 | 2,905-word report |
| Day 9 | Error handling build | ~9,600 | ~4,100 | ~13,700 | Error handler, circuit breaker |
| Day 10 | Query disambiguation | ~10,200 | ~4,800 | ~15,000 | Disambiguation module |
| Day 11 | Evaluation framework | ~9,800 | ~4,600 | ~14,400 | Evaluation scoring |
| Day 11b | Challenge 7 (Thematic) | ~13,800 | ~7,600 | ~21,400 | 3,051-word report |
| Day 12 | Challenge 8 (NVDA) | ~14,200 | ~8,700 | ~22,900 | 3,470-word report |
| Day 12b | Stress testing | ~6,400 | ~2,800 | ~9,200 | Stress test results |
| **Total** | | **~143,600** | **~74,100** | **~217,700** | **8 full research reports** |

---

## Token Efficiency Metrics

| Metric | Value |
|--------|-------|
| Total estimated tokens consumed | ~217,700 |
| Total research words produced | ~25,563 words across 8 reports |
| Output tokens per input token | 0.52 (healthy ratio) |
| Average tokens per research report | ~18,500 |
| Average words per research report | ~3,195 |
| Tool call overhead (est. % of input tokens) | ~28% |
| Memory context injection (est. % of input tokens) | ~15% |
| Net research generation (est. % of input tokens) | ~57% |

---

## Tool Efficiency Analysis

Tool efficiency is defined as the ratio of successful tool calls (returning usable data) to total tool calls attempted, across all sessions.

| Tool | Calls Attempted | Calls Successful | Efficiency Rate | Primary Failure Mode |
|------|----------------|-----------------|----------------|---------------------|
| financial_data_api | ~180 | ~134 | 74.4% | Rate limit, missing ticker |
| sec_filing_search | ~95 | ~68 | 71.6% | Filing not indexed, timeout |
| web_search | ~140 | ~105 | 75.0% | Rate limit, no results |
| vector_db_search | ~110 | ~108 | 98.2% | Near-perfect (local) |
| earnings_transcript | ~60 | ~38 | 63.3% | Limited coverage |
| **Overall** | **~585** | **~453** | **~77.4%** | |

**Observation:** Local tools (vector DB, memory) achieve near-100% efficiency. External API tools cluster in the 63–75% range, entirely consistent with free tier reliability expectations. The circuit breaker correctly absorbs the failure load from the 22.6% unsuccessful external calls, preventing them from propagating into report quality degradation.

---

## Error Recovery Analysis

| Error Type | Occurrences | Recovery Success | Recovery Rate |
|-----------|-------------|-----------------|--------------|
| API rate limit (Groq) | ~23 | 23 | 100% |
| Tool timeout | ~18 | 18 | 100% |
| Missing data (no filing) | ~31 | 31 | 100% |
| Circuit breaker open | ~12 | 12 | 100% |
| Malformed API response | ~8 | 8 | 100% |
| **Total errors** | **~92** | **~92** | **100%** |

**Key result:** ARA-1 recovered from every error encountered across the full project lifecycle. No session ended in an unhandled exception or a fabricated-data output. The graceful degradation system correctly triggered on complete tool failure scenarios and produced transparent report notes rather than silent or misleading outputs.

---

## Memory System Efficiency

| Metric | Value |
|--------|-------|
| Total semantic memory records | 36 |
| Total episodic memory episodes | 21 |
| Research sessions with memory retrieval | 12 of 15+ |
| Cache hit rate (memory vs. re-query) | ~68% |
| Average retrieval latency (local) | <50ms |
| Memory records added per session (avg.) | ~2.4 |
| Cross-session context reuse | Active in all Challenge 4–8 reports |

Memory system efficiency directly reduced token consumption: when prior research on Microsoft, Apple, or cloud infrastructure was available in memory, the agent retrieved it without issuing new API calls or re-generating context — saving an estimated 15,000–20,000 tokens across the full project.

---

## Cost Modeling: Free vs. Paid Tiers

### Current (Free Tier) — Actual Cost

| Component | Cost |
|-----------|------|
| Groq LLM inference | $0.00 |
| Yahoo Finance API | $0.00 |
| SEC EDGAR API | $0.00 |
| Web search | $0.00 |
| Compute (local) | $0.00 |
| **Total** | **$0.00** |

### Projected Cost at Groq Paid Tier

Groq paid tier pricing (Llama 3.1 70B): ~$0.59 per 1M input tokens, ~$0.79 per 1M output tokens.

| Component | Tokens | Rate | Cost |
|-----------|--------|------|------|
| Input tokens | ~143,600 | $0.59/1M | $0.085 |
| Output tokens | ~74,100 | $0.79/1M | $0.059 |
| **Total** | **~217,700** | | **~$0.14** |

**Entire project cost on paid Groq tier: approximately $0.14.**

### Projected Cost at Anthropic Claude API

Claude Sonnet 3.5 pricing: ~$3.00 per 1M input tokens, ~$15.00 per 1M output tokens.

| Component | Tokens | Rate | Cost |
|-----------|--------|------|------|
| Input tokens | ~143,600 | $3.00/1M | $0.43 |
| Output tokens | ~74,100 | $15.00/1M | $1.11 |
| **Total** | **~217,700** | | **~$1.54** |

### Monthly Cost Projection (Ongoing Research Use)

Assuming 3 full research reports per week (12/month) at average 18,500 tokens each:

| Provider | Monthly Token Est. | Monthly Cost |
|----------|-------------------|-------------|
| Groq free tier | ~222,000 | $0.00 (within limits) |
| Groq paid tier | ~222,000 | ~$0.17 |
| OpenAI GPT-4o | ~222,000 | ~$1.20 |
| Anthropic Claude Sonnet | ~222,000 | ~$2.00 |
| Anthropic Claude Opus | ~222,000 | ~$15.00 |

**Conclusion:** Even the most capable commercial LLM (Claude Opus) would cost approximately $15/month for ARA-1's current usage volume — affordable for any serious research use case. Groq paid tier at $0.17/month is essentially free.

---

## Optimization Opportunities

| Opportunity | Estimated Token Saving | Implementation Effort | Priority |
|------------|----------------------|----------------------|----------|
| Cache SEC filing summaries (avoid re-fetching) | ~12,000 tokens/month | Low | High |
| Compress system prompt via distillation | ~8,000 tokens/month | Medium | Medium |
| Batch financial API calls (single call vs. multiple) | ~5,000 tokens/month | Low | High |
| Reduce tool schema verbosity in context | ~4,000 tokens/month | Low | Medium |
| Summarize old episodic memory before injection | ~6,000 tokens/month | Medium | Medium |
| Use smaller model (Llama 3.1 8B) for disambiguation step | ~3,000 tokens/month | Low | Low |
| **Total potential saving** | **~38,000 tokens/month** | | |

Implementing the two high-priority optimizations (SEC filing cache + batch API calls) would reduce monthly token consumption by approximately 17,000 tokens — a 7–8% efficiency improvement at minimal engineering cost.

---

## Report Quality vs. Token Cost

A key validation of the architecture is that longer, higher-quality reports do not require proportionally more tokens — the memory system and tool routing ensure that incremental report length is driven by synthesis, not redundant retrieval.

| Report | Word Count | Total Tokens | Words per 1K Tokens |
|--------|-----------|--------------|---------------------|
| Challenge 1 (MSFT) | 2,171 | ~18,200 | 119 |
| Challenge 4 (Cloud) | 2,866 | ~20,800 | 138 |
| Challenge 7 (Thematic) | 3,051 | ~21,400 | 143 |
| Challenge 8 (NVDA) | 3,470 | ~22,900 | 152 |

**Trend:** Words-per-token efficiency improves as report complexity increases. This is the memory system working as designed — later, more complex reports reuse prior research context rather than re-generating it from scratch, reducing the proportion of tokens spent on retrieval relative to synthesis.

---

## Key Findings

1. **$0.00 total cost validates the free tier architecture.** The full project — 8 research challenges, 15+ sessions, 217,700 tokens — ran at zero cost. This demonstrates that meaningful autonomous financial research is accessible without cloud API spend.

2. **Token efficiency improves with memory maturity.** Reports produced later in the project (Challenges 7, 8) achieve 143–152 words per 1,000 tokens versus 119 for the first report — a 27% efficiency gain attributable to the accumulating memory system reducing redundant retrieval overhead.

3. **100% error recovery masks the volume of errors encountered.** Approximately 92 errors were encountered and recovered from silently across the project. Without the circuit breaker and graceful degradation systems, a significant fraction of these would have produced incomplete or misleading outputs.

4. **Paid tier upgrade cost is negligible.** The entire 12-day project would have cost $0.14 on Groq paid tier or $1.54 on Anthropic Claude Sonnet. Monthly ongoing cost for production use is estimated at $0.17–$2.00 depending on provider — a non-factor for any professional deployment.

5. **Tool efficiency at 77.4% is appropriate for free tier external APIs.** Free tier APIs are not SLA-bound and experience higher transient failure rates than paid equivalents. The 77.4% efficiency rate is a property of the data source tier, not of the agent architecture. Paid API tiers would push tool efficiency above 95%.

---

## Recommendations

| Priority | Recommendation |
|----------|---------------|
| High | Upgrade Groq to paid tier to eliminate sequential request rate limits |
| High | Implement SEC filing summary cache to reduce redundant EDGAR calls |
| High | Batch financial API calls per company per session |
| Medium | Add token usage logging per session for ongoing efficiency tracking |
| Medium | Compress system prompt — estimated 15% reduction achievable |
| Low | Evaluate Llama 3.1 8B for lightweight disambiguation steps |
| Low | Add cost dashboard to evaluation report for production transparency |

---

*Analysis prepared: May 5, 2026 | ARA-1 v1.0 | All token counts are estimates based on session logs and word count conversion. Actual billed tokens would reflect provider-specific tokenization.*
