# Standup Example

Captured from Apr 20, 2026 session. User asks for a daily standup summary.

---

## User Input

```
what should I work on today
```

(Alternative triggers: "standup", "what's on my plate", "what's blocked", "what's due")

---

## Prerequisites (silent, no output to user)

1. Identify user: `list_users` → find 최진호 (choijinho817)
2. Identify team: `list_teams` → Ball-space (single team, use silently)
3. Identify project: `list_projects` → Personal Sprint (single project, use silently)

---

## Data Gathering (silent)

1. `list_issues` with filters: assignee = user, status in [In Progress, Todo], project = Personal Sprint
2. Check for overdue items (due date < today)
3. Check for blocked items via `list_comments` on active tickets (last 48h)

---

## Output

### In progress

- **BAL-12** CUDA Graph Internals blog post (Medium) — research notes drafted, writing pending
- **BAL-11** vAttention applicability analysis (Medium) — parallel research subagents completed, document draft in progress
- **BAL-7** Conclave 감상 보고서 (High) — report draft at 2,980 chars, due Apr 29
- **BAL-13** micro-vllm inference engine (High) — architecture defined, implementation not started

### Due soon

- **BAL-7** Conclave 감상 보고서 — due Apr 29 (9 days)

### Blocked / needs attention

None identified.

### Recommended focus

Start with BAL-7 (Conclave report) — it's the only time-boxed item with a hard deadline, and the draft is already 74% complete.

Want to dig into any of these, or move on?

---

## Format Rules

- Three sections: **In progress**, **Due soon / Blocked**, **Recommended focus**
- One line per ticket: `**TICKET-ID** title (priority) — short state note`
- End with a focus recommendation and a yes/no prompt
- No tables, no emoji indicators, no dashboard formatting
- No writes happen in this workflow
