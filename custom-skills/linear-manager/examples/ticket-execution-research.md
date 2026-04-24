# Ticket Execution Example: Research / Analysis

Captured from Apr 19, 2026 session. User asks to investigate a ticket and produce a Linear document.

---

## User Input

```
https://linear.app/ball-space/issue/BAL-11/analyze-vattention-strengths-and-applicability-to-modern-llm
```

(Alternative triggers: "investigate BAL-11", "work on BAL-11", "dig into this ticket", "research BAL-11 and write up findings")

---

## Step 1: Fetch the ticket (silent)

`get_issue` on BAL-11. Extract:
- Title: "Analyze vAttention strengths and applicability to modern LLM architectures"
- Status: Todo, Priority: Medium, Assignee: 최진호
- Description: acceptance criteria requiring per-architecture verdicts
- Comments: none

---

## Step 2: Confirm scope with user

Since this is a research/analysis ticket, confirm the depth:

```
BAL-11 asks for a vAttention applicability analysis across three architectures
(Gated Delta Net, hybrid Mamba, sliding window attention). I'll research each
and write up a Linear document with per-architecture verdicts.

Should I also update the ticket status to In Progress?
```

User: `yes`

→ `save_issue` to transition BAL-11 from Todo to In Progress.

---

## Step 3: Do the work

Launch parallel research (scientist subagents or direct web search):
1. vAttention paper mechanics (arXiv 2405.04437): CUDA VMM APIs, demand paging, FlashAttention compatibility
2. Gated Delta Net: state representation, whether traditional KV cache exists
3. Hybrid Mamba+attention: partial applicability analysis
4. Sliding window attention: KV cache eviction patterns, circular buffer implementation

Collect findings before drafting.

---

## Step 4: Present in-chat summary + document draft

### In-chat summary (short, 1-2 paragraphs)

```
Finished the vAttention analysis. Key finding: vAttention is fully applicable
to standard transformer attention and sliding window variants (they maintain
explicit KV caches that benefit from virtual memory management). It's partially
applicable to Mamba hybrids (only the attention layers benefit). Not applicable
to Gated Delta Net — it uses a fixed-size recurrent state matrix instead of a
KV cache, so vAttention's premise doesn't apply.

Here's the full document draft:
```

### Document draft

```markdown
# vAttention: Technical Analysis & Applicability to Modern LLM Architectures

## Summary

vAttention (arXiv 2405.04437, ASPLOS 2025) replaces PagedAttention's
software-level memory management with OS-level virtual memory via CUDA VMM
APIs. This document analyzes its applicability to three non-standard
architectures.

## Context

BAL-11 requests per-architecture verdicts for: Gated Delta Net, hybrid
Mamba+attention, and sliding window attention. The analysis is grounded in the
original paper's benchmarks showing up to 1.97x throughput over vLLM.

## Findings

### Gated Delta Net — Not Applicable
[analysis with reasoning...]

### Hybrid Mamba+Attention — Partially Applicable
[analysis with reasoning...]

### Sliding Window Attention — Fully Applicable
[analysis with reasoning...]

## Open Questions / Next Steps

- Benchmark vAttention with sliding window on long-context models (128K+)
- Investigate whether Mamba-2's larger state benefits from VMM-style allocation
```

### Proposed comment

```
Investigation writeup: vAttention Technical Analysis & Applicability to Modern
LLM Architectures. TL;DR: fully applicable to sliding window, partially to
Mamba hybrids (attention layers only), not applicable to Gated Delta Net
(no KV cache).
```

### Confirmation prompt

```
Create the document (attached to BAL-11) and post the comment?
```

---

## Step 5: On user approval

1. `create_document` with `issue: "BAL-11"` (NOT `project:`). Title: "vAttention: Technical Analysis & Applicability to Modern LLM Architectures"
2. `save_comment` on BAL-11 with the comment text + document link
3. Report back with document URL and comment confirmation

```
Done:
- Document created: https://linear.app/ball-space/document/vattention-technical-analysis-...
- Comment posted on BAL-11 with link to document

The ticket stays In Progress. Want me to change the status or move on?
```

**Do NOT move ticket to Done.** Only suggest status change if user explicitly asks.

---

## Format Rules

- Always fetch ticket first, confirm scope if ambiguous
- In-chat summary: 1-2 paragraphs, headline conclusion
- Document draft: shown in full before creation
- Proposed comment: shown before posting
- Explicit confirmation before any write (`create_document`, `save_comment`)
- `create_document` uses `issue:` parameter, never `project:`
- Never move ticket to Done without explicit user request
- One document per user request
