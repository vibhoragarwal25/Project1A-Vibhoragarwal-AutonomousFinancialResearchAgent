# ARA-1: Autonomous Financial Research Agent

**Project:** 1A — Agentic AI Engineer
**Developer:** Vibhoragarwal
**Timeline:** 15 Days

---

## Overview

ARA-1 is a fully autonomous AI agent that replicates the research workflow of a junior financial analyst. Given a research query, ARA-1 independently formulates a research plan, gathers data from multiple sources, resolves conflicting information, and synthesizes findings into a professional investment research report — without step-by-step human guidance.

The agent completed 8 research challenges covering investment analysis, earnings analysis, risk assessment, competitive analysis, contradiction resolution, sector analysis, and thematic synthesis. All 8 challenges passed evaluation. Total infrastructure cost: **$0.00**.

---

## Architecture

ARA-1 implements a hybrid ReAct and Plan-and-Execute architecture:

```
Query Input
    │
    ▼
┌─────────────────────────────────┐
│     Query Disambiguation        │  ← Resolves ambiguous queries before research
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│     Research Planner            │  ← Creates structured plan before tool calls
│  (Plan-and-Execute outer loop)  │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│     ReAct Execution Loop        │  ← Thought → Action → Observation cycles
│                                 │
│  ┌──────────┐  ┌─────────────┐  │
│  │  Memory  │  │ Tool Router │  │
│  │  System  │  │             │  │
│  └──────────┘  └─────────────┘  │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│     Synthesis Engine            │  ← Cross-source analysis, conflict resolution
└─────────────────────────────────┘
    │
    ▼
  Research Report Output
```

**Key architectural decisions:**

- **Plan before execute:** Agent creates a structured research plan before issuing any tool calls, reducing redundant calls from 15+ to 5–7 per session
- **Memory-first retrieval:** Prior research is checked before any API call, saving 33–40% of tokens on follow-on queries
- **Circuit breaker pattern:** Tools that fail 3 consecutive times are bypassed for 60 seconds, preventing cascade failures
- **Graceful degradation:** When all tools fail, the agent generates a transparent report with explicit data gap disclosure rather than fabricating data
- **Source reliability hierarchy:** SEC filings (Tier 1) outweigh news sentiment (Tier 4) in conflict resolution

---

## Capabilities

| Capability | Description |
|-----------|-------------|
| Investment research | Full buy/hold/sell reports with price targets, valuation, and risk assessment |
| Earnings analysis | Beat/miss analysis, management commentary, forward guidance synthesis |
| Risk assessment | Multi-dimensional risk scoring with mitigation factor analysis |
| Competitive analysis | Cross-company comparison with market share, margin, and positioning data |
| Contradiction detection | Identifies and resolves divergence between financial data and news sentiment |
| Query disambiguation | Resolves ambiguous queries using context before initiating research |
| Thematic synthesis | Cross-company pattern recognition drawing on accumulated memory |
| Graceful degradation | Transparent data gap disclosure when tools fail — never fabricates data |

---

## Technical Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| LLM | Groq (Llama 3.3 70B) | Free tier |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 | Free (local) |
| Vector database | ChromaDB | Free (local) |
| Financial data | Yahoo Finance (yfinance) | Free |
| Financial data (primary) | Financial Modeling Prep API | Free tier |
| SEC filings | SEC EDGAR public API | Free |
| News/web search | DuckDuckGo API | Free |
| Memory persistence | JSON flat-file + ChromaDB | Free (local) |
| **Total** | | **$0.00** |

---

## Results

### Challenge Outcomes

| Challenge | Topic | Report Length | Evaluation Score | Result |
|-----------|-------|--------------|-----------------|--------|
| 1 | Microsoft investment report | 2,171 words | 78.1/100 | ✅ Pass |
| 2 | Apple Q1 FY2025 earnings | 2,250 words | 78.1/100 | ✅ Pass |
| 3 | Tesla risk assessment | 2,290 words | 78.1/100 | ✅ Pass |
| 4 | Cloud infrastructure comparison | 2,866 words | 78.1/100 | ✅ Pass |
| 5 | Palantir contradiction analysis | 2,560 words | 78.1/100 | ✅ Pass |
| 6 | Banking sector analysis | 2,905 words | 78.1/100 | ✅ Pass |
| 7 | Tech sector thematic analysis | 3,051 words | 78.1/100 | ✅ Pass |
| 8 | NVIDIA investment report | 3,470 words | 78.1/100 | ✅ Pass |

### System Metrics

| Metric | Value |
|--------|-------|
| Challenges passing | 8/8 (100%) |
| Average report length | 2,695 words |
| Tool efficiency rate | 77.4% |
| Error recovery rate | 100% |
| Data fabrication events | 0 |
| Memory records accumulated | 36 |
| Episodic memory episodes | 21 |
| Research sessions completed | 15+ |
| Total tokens consumed (est.) | ~217,700 |
| Total project cost | $0.00 |

### Before vs After Optimization

| Metric | Day 1 Baseline | Day 13 Final | Improvement |
|--------|---------------|-------------|-------------|
| Report quality score | 41/100 | 78.1/100 | +90% |
| Tool efficiency | ~34% | 77.4% | +2.3x |
| Error recovery | 0% | 100% | Complete |
| Hallucination rate | ~23% | <2% | -90% |
| Tool calls per session | 15+ | 5–7 | -60% |

---

## Key Optimizations

Ten optimizations were implemented during the build. Full details in [`docs/optimization_log.md`](docs/optimization_log.md).

| # | Optimization | Impact |
|---|-------------|--------|
| 1 | Hybrid ReAct + Plan-and-Execute | Tool calls reduced from 15+ to 5–7 |
| 2 | Exponential backoff error handler | Error recovery: 0% → 100% |
| 3 | Circuit breaker pattern | Cascade failures eliminated |
| 4 | Local embeddings (sentence-transformers) | Zero cost memory search |
| 5 | Yahoo Finance fallback | Financial data always available |
| 6 | Tool parameter prompt engineering | Tool errors reduced to 0 in Ch. 7+ |
| 7 | Context window management | Coherence across long sessions |
| 8 | Episodic memory for strategy learning | 21 episodes, applied to new queries |
| 9 | Source reliability hierarchy | Conflict resolution accuracy improved |
| 10 | Report quality prompt engineering | Score: 57.2 → 78.1 average |

---

## Project Structure

```
ARA-1/
├── agent/
│   ├── core.py              # Main ARA1Agent class, ReAct loop
│   ├── llm.py               # LLM provider (Groq) with retry logic
│   ├── prompts.py           # System, planning, and synthesis prompts
│   ├── circuit_breaker.py   # Circuit breaker implementation
│   ├── error_handler.py     # Exponential backoff + graceful degradation
│   ├── fallback_chains.py   # Tool fallback chains and confidence scoring
│   ├── disambiguation.py    # Query disambiguation engine
│   ├── query_analyzer.py    # Query type classification
│   ├── parser.py            # ReAct output parser
│   └── logger.py            # Structured agent logging
├── memory/
│   ├── vector_store.py      # Semantic memory (ChromaDB + sentence-transformers)
│   ├── episodic.py          # Episodic strategy memory across sessions
│   └── context_manager.py  # Context window management
├── tools/
│   ├── __init__.py          # Tool registry
│   ├── financial_api.py     # FMP + Yahoo Finance financial data
│   ├── sec_edgar.py         # SEC EDGAR filing retrieval
│   ├── web_search.py        # DuckDuckGo web search
│   ├── failure_injector.py  # Testing: simulated tool failures
│   └── ...                  # Additional tools (earnings, peers, sentiment)
├── results/
│   ├── challenge_1.md       # Microsoft investment report
│   ├── challenge_2.md       # Apple earnings analysis
│   ├── challenge_3.md       # Tesla risk assessment
│   ├── challenge_4.md       # Cloud infrastructure comparison
│   ├── challenge_5.md       # Palantir contradiction analysis
│   ├── challenge_6.md       # Banking sector analysis
│   ├── challenge_7.md       # Tech thematic analysis
│   ├── challenge_8.md       # NVIDIA investment report
│   ├── evaluation_report.md # Full evaluation results
│   ├── stress_test_report.md
│   └── token_usage_analysis.md
├── docs/
│   ├── architecture_specification_final.md
│   ├── optimization_log.md  # 10 optimizations with evidence
│   └── trace_gallery.md     # 6 annotated reasoning traces
├── logs/
│   ├── episodic_memory.json # 21 cross-session strategy episodes
│   └── session_*.json       # Per-session execution logs
├── stress_test.py
├── token_analysis.py
├── requirements.txt
└── README.md
```

---

## API Keys Required

| Key | Where to Get | Cost |
|-----|-------------|------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — create account, go to API Keys | Free tier |
| `FMP_API_KEY` | [financialmodelingprep.com/developer](https://financialmodelingprep.com/developer/docs/) — register for free tier | Free tier (250 req/day) |

All other data sources (SEC EDGAR, Yahoo Finance, DuckDuckGo) require no API key.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Vibhoragarwal/Project1A-Vibhoragarwal-AutonomousFinancialResearchAgent
cd Project1A-Vibhoragarwal-AutonomousFinancialResearchAgent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=your_groq_api_key
export FMP_API_KEY=your_fmp_api_key
```

---

## How to Run a Research Query

```python
from agent.core import ARA1Agent

agent = ARA1Agent()
report = agent.research('Analyze Microsoft investment thesis', urgency='standard')
print(report)
```

Valid `urgency` values:
- `'standard'` — full research, 10–15 tool calls (default)
- `'urgent'` — faster research, capped at 10 tool calls
- `'critical'` — rapid summary, capped at 5 tool calls

---

## Running the Challenges

```bash
# Run all 8 challenges and generate evaluation report
python regenerate_reports.py

# Run stress test
python stress_test.py

# Run token analysis
python token_analysis.py
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/architecture_specification_final.md`](docs/architecture_specification_final.md) | Full system architecture specification |
| [`docs/optimization_log.md`](docs/optimization_log.md) | 10 optimizations with before/after evidence |
| [`docs/trace_gallery.md`](docs/trace_gallery.md) | 6 annotated agent reasoning traces |
| [`results/evaluation_report.md`](results/evaluation_report.md) | Challenge evaluation scores and methodology |
| [`results/stress_test_report.md`](results/stress_test_report.md) | Stress test results across 4 test types |
| [`results/token_usage_analysis.md`](results/token_usage_analysis.md) | Token consumption and cost analysis |

---

## Evaluation Methodology

Reports are scored on 5 dimensions:

| Dimension | Weight | What is Measured |
|-----------|--------|-----------------|
| Data accuracy | 25% | Factual correctness, numerical precision |
| Source diversity | 20% | Multiple source types (SEC, API, news, memory) |
| Analytical depth | 25% | Insight quality, contradiction resolution, synthesis |
| Report completeness | 20% | Coverage of required sections and topics |
| Error recovery | 10% | Transparent handling of tool failures |

**Passing threshold:** 70/100. All 8 challenges scored 78.1/100.

---

## Design Principles

**1. Never fabricate data.** When tools fail, the agent discloses data gaps explicitly. No hallucinated revenue figures, market share estimates, or price targets appear in any report without a cited source.

**2. Memory before API.** Prior research is checked in semantic memory before any external API call. This reduces token consumption, avoids rate limits, and produces more consistent cross-report analysis.

**3. Plan before execute.** A structured research plan is created before any tool is called. This prevents the redundant tool call patterns common in naive ReAct implementations.

**4. Transparency over confidence.** When data confidence is medium or low (due to tool fallbacks), this is explicitly stated in the report. A transparent medium-confidence report is more valuable than a confident hallucinated one.

**5. Zero-cost architecture.** Every component uses a free tier or locally-run model. Production-grade autonomous financial research is achievable at $0.00 in infrastructure cost.

---

## AI Tools Used

| Tool | Role |
|------|------|
| **Claude Code** (Anthropic) | Primary coding assistant used throughout the 15-day build — architecture design, debugging, code review, and documentation |
| **Groq API** (Llama 3.3 70B) | Runtime LLM powering the agent's reasoning, planning, and synthesis in every research session |
| **sentence-transformers** (all-MiniLM-L6-v2) | Local embedding model for semantic similarity search in the vector memory store |
| **ChromaDB** | Local vector database for storing and retrieving semantic research memory |

---

*ARA-1 v1.0 | Built in 15 days | Total cost: $0.00*
