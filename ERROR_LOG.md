cat > ERROR_LOG.md << 'EOF'
# ERROR LOG — ARA-1 Project Document Errors

## Error 1 — Section A6.2: Source Reliability Hierarchy Inverted
**Location:** Part A, Section A6.2, Tier 4 and Tier 5
**Error:** Major news outlets (Reuters, Bloomberg, FT) placed at Tier 5,
below social media at Tier 4. This is inverted.
**Correct:** Professional journalism should be Tier 4,
social media/anonymous forums should be Tier 5.

## Error 2 — Section A5.2: AB-4 Memory Utilization Formula Wrong
**Location:** Part A, Section A5.2, Category 5, metric AB-4
**Error:** States metric is calculated as memory_hits MULTIPLIED BY
total_api_calls. Should be DIVIDED BY (ratio not product).
**Correct:** memory_utilization = memory_hits / total_api_calls

## Error 3 — Section A7.3: SCAP Historical Facts Wrong
**Location:** Part A, Section A7.3
**Error:** States SCAP conducted in 2007 following Dodd-Frank Act.
SCAP was conducted in 2009 and Dodd-Frank was signed in 2010.
**Correct:** SCAP conducted in 2009 as response to 2008 financial crisis.

## Error 4 — Section C4.2: Form 20-F Misattributed to MCA
**Location:** Part C, Case Study 4, Section C4.2
**Error:** States Indian companies file Form 20-F with MCA.
Form 20-F is an SEC form for foreign private issuers on US exchanges.
**Correct:** Indian MCA annual return uses Form MGT-7, 
financial statements use AOC-4.

## Error 5 — Section B3.1: Five Dimensions Claimed, Four Shown
**Location:** Part B, Section B3.1
**Error:** Text states challenges scored across five dimensions
but scoring matrix only shows four columns.
**Correct:** Either five columns should be shown or text should say four.

## Error 6 — Section B4.4: Earnings Transcript Unlock Contradiction
**Location:** Part B, Section B4.4
**Error:** earnings_transcript tool unlocked only after Challenge 2,
but Challenge 2 lists earnings_transcript as a required tool.
Logical contradiction — tool needed to complete C2 but granted after C2.

## Error 7 — Section E2.2: text-embedding-3-large Dimensions Wrong
**Location:** Part E, Section E2.2
**Error:** States text-embedding-3-large has 1024 dimensions.
**Correct:** OpenAI text-embedding-3-large default is 3072 dimensions.
1024 is Cohere embed-v3, listed in the very next bullet point.
EOF