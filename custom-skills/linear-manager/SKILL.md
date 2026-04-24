---
name: linear-manager
description: 'A personal sprint secretary for managing Linear tickets via the Linear MCP. Covers seven workflows: standup summaries, ticket triage, sprint planning, ticket hygiene, ticket writing, team retrospectives, and ticket execution (investigation/implementation work, written up as Linear documents attached to the issue). Trigger whenever the user''s request involves Linear tickets or sprint workflows in a substantive way — reviewing what''s on their plate, cleaning up tickets, triaging a backlog, planning or wrapping a sprint, drafting a new ticket, prepping a retrospective, or asking you to investigate/plan/implement work on a specific ticket. Explicit "/linear-manager" invocation is supported but not required. Use proactively when the context fits — "what should I work on today", "clean up my stale tickets", "investigate ENG-142 and write up findings", "draft a ticket for this bug", "help me plan next sprint". Skip only for purely conversational Linear mentions that don''t ask for any workflow action.'
---
 
# Linear Manager
 
A personal secretary for the user's Linear workspace. Helps the user run seven recurring workflows against their Linear tickets: **standup**, **triage**, **sprint planning**, **hygiene**, **ticket writing**, **retrospective**, and **ticket execution**.
 
---
 
## Triggering — read this first
 
Use this skill whenever the user's request maps to one of the seven workflows below — even if they didn't explicitly say "/linear-manager". Examples of requests that should trigger this skill:
 
- "What should I work on today?" → standup
- "Can you clean up my stale tickets?" → hygiene
- "Triage my untriaged tickets" → triage
- "Help me plan next sprint" / "wrap up this sprint" → sprint planning
- "Make a ticket for this bug" / "turn this into a ticket" → ticket writing
- "Prep retro talking points" → retrospective
- "Investigate ENG-142 and write up what you find" / "work on this ticket" / "plan out the implementation for ENG-50" → ticket execution
Explicit invocation like `/linear-manager` still works and forces this skill on. When the user's request is ambiguous ("help me with my sprint"), ask one short clarifying question.
 
**When NOT to use this skill:** purely conversational Linear mentions with no workflow action attached ("Linear has been buggy today", "my sprint was rough, just venting") — handle those normally.
 
Once engaged, stay in linear-manager mode for related follow-ups unless the user clearly changes topics.
 
---
 
## Prerequisites — do these once per conversation
 
Before the first workflow runs, establish two things. Do this quietly (don't announce it as "setup"); just resolve them and move on.
 
### 1. Identify the user in Linear
 
Most workflows need "my tickets." Try in this order:
 
1. Use `assignee=me` or equivalent in Linear MCP filters if supported.
2. If that fails, call `list_users` and find the current user by name/email context from the conversation.
3. If still ambiguous, ask the user: "Which Linear user are you? (name or email)"
Remember the answer for the rest of the conversation.
 
### 2. Identify the team and project
 
The skill assumes one team and one project. To confirm:
 
1. Call `list_teams`. If there's exactly one team, use it silently.
2. If there are multiple teams, ask: "Which team are we working in? (options: X, Y, Z)"
3. Do the same with `list_projects` scoped to that team. One project → use it. Multiple → ask.
Remember both for the rest of the conversation.
 
If the user invokes a workflow that doesn't need a project (e.g., some ticket-writing requests are team-scoped), don't force project selection.
 
---
 
## Workflow selection
 
When the user's request lands in linear-manager territory, infer which workflow they want using these anchors:
 
| Workflow | Typical phrasings |
|---|---|
| **Standup** | "standup", "what should I work on", "what's on my plate", "what's blocked", "what's due" |
| **Triage** | "triage", "inbox", "un-triaged", "untriaged", "needs priorities", "needs labels" |
| **Sprint planning** | "plan the sprint", "next sprint", "wrap up the sprint", "sprint plan" |
| **Hygiene** | "clean up", "stale", "tidy", "missing acceptance criteria", "stuck tickets" |
| **Ticket writing** | "make a ticket", "new ticket", "draft a ticket", "turn this into a ticket", "file a ticket" |
| **Retrospective** | "retro", "retrospective", "what happened last sprint", "prep for retro meeting" |
| **Ticket execution** | "work on TICKET-N", "investigate TICKET-N", "handle this ticket", "plan out the implementation for X", "dig into this ticket", "figure out what to do about TICKET-N", "implement TICKET-N" |
 
**If the request is ambiguous** (e.g., "help me with my sprint"), ask one short clarifying question with 2–3 options. Don't guess when it's genuinely unclear — but do guess when the intent is obvious.
 
---
 
## Confirmation model — applies to every workflow
 
This skill **drafts and proposes, the user approves, then the skill writes to Linear.** No autonomous writes.
 
Confirmation is **per-ticket**: show one ticket's proposed changes, get a yes/no/edit, then move to the next. Accept these replies:
 
- `yes`, `y`, `ok`, `confirm` → apply the change, move to next
- `no`, `n`, `skip` → discard, move to next
- `edit` / "change X to Y" → update the draft, re-show, re-confirm
- `stop` / `done` → bail out of the batch
Never batch-confirm multiple tickets. Never write without an explicit yes.
 
For read-only operations (standup, retrospective, parts of triage/hygiene that only surface info), no confirmation is needed — just present the output.
 
### Hard rule: never mark a ticket Done without explicit approval
 
This is the single most important write-boundary in this skill. **Never** transition a ticket to "Done" (or any equivalent terminal/completed status like "Completed", "Closed as done", "Shipped") on your own initiative.
 
This rule applies everywhere — including the ticket execution workflow, where it is tempting to "close out" a ticket after finishing investigation or implementation. Don't. Writing a summary document, posting a comment, updating the description, or moving to an intermediate state like "In Review" is fine with the normal per-ticket confirmation. Moving to Done specifically requires the user to **explicitly** say something like "mark it done", "close it", "move ENG-142 to done". Generic approvals like "yes", "looks good", or "go ahead" that come in response to a proposal that did not itself mention the Done transition do **not** count.
 
If you're unsure whether a user approval was scoped to the Done transition, ask. "Should I also move the ticket to Done, or leave it in its current status?" is a good check.
 
---
 
## Output conventions
 
All workflow outputs follow these conventions:
 
- **Prose-first.** Short sentences and short lists. Avoid big tables, emoji indicators, or dashboard-style formatting.
- **End with a proposed next action.** Every output closes with something the user can say "yes" to. E.g., a standup ends with "Want me to focus you on X first?" A triage ends with the first ticket's proposed changes awaiting confirmation. A retro ends with "Want these as talking points for your team meeting?"
- **Reference tickets by identifier + short title**, e.g., "ENG-142 (Fix OAuth redirect loop)".
---
 
## Workflow 1: Standup
 
**Intent:** the user wants a quick "what's on my plate today" summary.
 
**Steps:**
1. Fetch issues assigned to the user that are In Progress or Todo with recent activity.
2. Fetch issues where the user is mentioned or where blocking/blocked relationships apply (use `list_issues` with appropriate filters; inspect comments via `list_comments` for the last 24–48h if relevant).
3. Identify overdue items (due date passed, status not Done).
**Output shape:** three short sections, then a focus recommendation:
 
- **In progress** — 1 line per ticket: ID, title, current status, a 3–6 word note on state if obvious from recent activity.
- **Blocked / needs attention** — 1 line per ticket with *why* (blocker identified from comments, mentions, or status).
- **Due soon** — tickets with due dates within ~3 days.
- **Recommended focus** — one sentence: "Start with X because Y."
End with: "Want to dig into any of these, or move on?"
 
No writes happen in this workflow.
 
---
 
## Workflow 2: Triage
 
**Intent:** the user wants un-triaged tickets reviewed and fixed up.
 
**Steps:**
1. On first triage use this conversation, call `list_issue_labels` and note the actual label taxonomy. Use only labels from that set — never invent labels.
2. Find issues missing one or more of: priority, labels, estimate, assignee. Use `list_issues` with appropriate filters.
3. For each, propose values based on title + description content and a one-line rationale for each proposal.
**Output shape:**
- A brief header naming how many un-triaged tickets were found.
- Then show the first ticket: ID, title, short description excerpt, proposed priority / labels / estimate / assignee, rationale.
- Wait for confirmation. Apply with `save_issue` or the equivalent Linear MCP update tool.
- Move to the next ticket.
Keep the total session manageable — if there are more than ~10 un-triaged tickets, surface the count upfront and offer to do them in chunks.
 
---
 
## Workflow 3: Sprint planning
 
**Intent:** the user wants to close out the current sprint/cycle and plan the next.
 
**Steps:**
1. Identify the active cycle and the next cycle. Use `list_cycles` for the team.
2. For the ending cycle: count shipped (Done), carried over (still open), dropped (closed without shipping).
3. For the next cycle: propose which currently-open tickets to pull in, prioritized by urgency and rough capacity (use existing estimates where present).
**Output shape:** two short parts.
 
- **Sprint recap (personal).** Brief: "X shipped, Y carried over, Z dropped." Name the notable items. This is a *personal* recap — the team-facing version lives in the retrospective workflow, don't duplicate.
- **Next sprint proposal.** List of tickets proposed to pull into the next cycle, with a one-line rationale each. Estimate the total load if estimates are available.
End with: "Want me to move these into the next cycle? I'll confirm one at a time."
 
If the user confirms, apply cycle assignments with per-ticket confirmation.
 
---
 
## Workflow 4: Hygiene
 
**Intent:** the user wants stale/unhealthy tickets cleaned up.
 
**Steps:** find tickets matching any of:
 
- **Stale:** no activity in 14+ days, status is not Done/Cancelled.
- **Missing acceptance criteria:** description lacks a criteria section (heuristic: no bulleted "acceptance criteria", "AC:", or similar).
- **Status mismatch:** In Progress but no updates in 7+ days; or Todo but assigned and old.
- **Unowned:** in an active cycle with no assignee.
**Output shape:**
- Group by category. Each category shows a count and a short list (ID + title + the reason it was flagged).
- For each ticket, propose an action: "move to Needs Review", "add missing acceptance criteria draft", "unassign", "close as stale — ask before this one", etc.
- Per-ticket confirmation. Destructive proposals (closing tickets) always require explicit yes — never default.
---
 
## Workflow 5: Ticket writing
 
**Intent:** the user wants to turn rough input into a well-formed Linear ticket.
 
**Info-gathering is adaptive:**
- If the user's input is detailed (symptom, expected behavior, context, urgency hint all present), draft directly.
- If the input is sparse ("new ticket: auth bug"), ask **2–3 short clarifying questions** before drafting. Good questions: What's the symptom? What should happen instead? How urgent? Who's affected?
**On first ticket-writing use this conversation**, call `list_issue_labels` to get the real workspace label set. Only suggest labels from that set.
 
**Draft template:**
 
- **Title** — imperative, concise, scannable.
- **Description** — 2–4 sentences: what, why it matters, context.
- **Acceptance criteria** — bulleted, testable conditions.
- **Labels** — from the workspace set, with brief rationale.
- **Priority** — with rationale.
- **Estimate** — only if enough detail is available to guess; otherwise omit.
- **Assignee** — default to the user unless they say otherwise.
**Output shape:** show the full draft as a preview. Then: "Create this ticket, or want to edit?"
 
Accept edits inline ("change priority to Low", "drop the frontend label", "add acceptance criterion: works on Safari 17+"). Re-show the draft after each edit. Only create on explicit yes. Use `save_issue`.
 
---
 
## Workflow 6: Retrospective
 
**Intent:** the user wants to prepare for a **team retrospective meeting** — so this is framed for team discussion, not personal reflection.
 
**Steps:**
1. Scope to the cycle that just ended (or is ending today). Confirm with the user if ambiguous.
2. Gather:
   - What shipped (Done in this cycle).
   - What slipped (carried over or dropped).
   - Recurring blockers (comments mentioning "blocked", "waiting on", dependency tickets).
   - Churn (tickets with many status transitions, or long time-in-status — a rough proxy for thrash).
   - Notable patterns (same label/area repeatedly blocked; several tickets slipping for the same reason).
**Output shape:** talking points formatted for a team meeting. Keep it presentable — the user may paste this into a doc or read it aloud.
 
- **Shipped** — headline count + notable items.
- **Slipped** — what didn't land and why (one line each).
- **Blockers & churn** — patterns, not individual tickets, unless a specific ticket is notable.
- **Suggested discussion prompts** — 2–4 open questions the team could dig into ("Why did auth tickets keep bouncing between review and in-progress?").
End with: "Want this reformatted as bullet points for a deck, or as a doc?"
 
No writes happen in this workflow.
 
---
 
## Workflow 7: Ticket execution
 
**Intent:** the user hands you a specific Linear ticket and asks you to do the work on it — either investigation/planning/analysis, or actual implementation, or both. Your job is to do the work, write the results up as a **Linear document attached to the issue**, and post a comment on the ticket pointing at it. The ticket itself stays open under the user's control.
 
**Scope is flexible.** "Execution" here ranges from a planning writeup ("figure out how we'd build this and write up a plan") to deeper implementation work ("investigate the bug and propose a fix", or actually draft the code changes). Match the depth to what the user asked for:
 
- **Investigation/analysis/planning** — read the ticket, look at related code/docs/tickets, identify causes or constraints, lay out options or a recommended approach.
- **Implementation** — in addition to the above, produce the concrete change (code, config, copy, whatever the ticket calls for). If you're in an environment with PR tooling and the user wants it, you can go as far as preparing a PR — but the Linear-side outputs (document + comment) still happen.
If the user's ask is ambiguous between "plan it" and "build it", ask one short clarifying question before diving in.
 
### Steps
 
1. **Fetch the ticket.** Use `get_issue` on the ticket ID the user named. Pull its description, acceptance criteria, labels, current status, and recent comments. If the user referred to a ticket vaguely ("that auth ticket"), confirm which one before proceeding.
2. **Do the work** at the depth the user asked for. Use whatever tools fit — code search, file reading, web search, other MCP tools. Keep a running mental list of what you did and found; you'll need it for the document.
3. **Draft a Linear document** summarizing the work (see template below). Show the draft to the user in chat first. Do not create the document until the user confirms.
4. **On approval, create the document attached to the issue.** Call `create_document` and pass the `issue` parameter with the ticket ID (e.g., `issue: "ENG-142"`). **Do not pass the `project` parameter** — documents in this workflow are scoped to the ticket, not the project, so they live under the issue's own resources. Choose a clear title: `[TICKET-ID] <what this document covers>`, e.g. `[ENG-142] Investigation: OAuth redirect loop` or `[ENG-50] Implementation plan: webhook retry policy`.
5. **Post a comment on the ticket** linking the new document, using `save_comment`. Keep the comment short — one or two sentences describing what the document contains — and include a link/reference to the document. Example: "Investigation writeup: [ENG-142] Investigation: OAuth redirect loop. TL;DR: the loop is caused by the stale `state` cookie; see the doc for the proposed fix."
6. **Do not change the ticket's status** unless the user explicitly asks. **Especially never move it to Done.** See the hard rule in the Confirmation Model section above. If it feels natural to suggest a status change (e.g., "this looks ready for review — want me to move it to In Review?"), you may propose it, but wait for an explicit yes before applying.
### Why issue-scoped, not project-scoped
 
The document is a writeup of work done on **this specific ticket**. Attaching it to the issue keeps it alongside the ticket's other resources (comments, attachments, related links), so anyone reading the ticket later sees the writeup in context. Scoping it to the project instead would dump it into a general project-docs bucket, losing the ticket association and making it harder to find. Always use `issue:` here — never `project:`.
 
### One document per user request
 
Each separate "please do X on this ticket" request produces **one** Linear document. If the user first asks for a plan, you create a planning document. If they later ask for the implementation, you create a **second** document for that — don't overwrite or append to the first. Each document stands alone, is attached to the same issue, and gets its own comment on the ticket.
 
If the user explicitly asks you to extend an existing document instead of creating a new one, use `update_document` — but default is: new request → new document.
 
### Document template
 
Structure the document to match the kind of work done. A reasonable default:
 
- **Summary** — 2–4 sentences: what was asked, what this document covers, headline conclusion.
- **Context** — the ticket's current state, relevant background, anything you needed to know going in.
- **What I looked at / did** — files, code paths, related tickets, external sources. Concrete enough that the user could retrace the steps.
- **Findings / proposal / changes** — the substance. For investigation, this is the analysis and recommendation. For implementation, this is the description of the change (and, if applicable, a pointer to the PR or the diff).
- **Open questions / next steps** — anything unresolved, and the obvious follow-ups.
Adjust section names and depth to fit the work — don't force the template where it doesn't serve the content.
 
### Output shape (in chat)
 
After you've done the work:
 
1. A short in-chat summary of what you found/did (a paragraph or two — enough for the user to decide without opening the document).
2. The full document draft, so they can review it before it's created.
3. The proposed comment text.
4. Ask: "Create the document (attached to TICKET-ID) and post the comment?"
On approval, create the document with `issue: "TICKET-ID"`, then post the comment. Report back with both links/references. Then — and only then — if it seems relevant, you may ask whether the user wants any status change on the ticket. **Never apply a Done transition without an explicit, scoped yes.**
 
---

## Conversation logging (CLAUDE.md per issue)

**Intent:** Every time a Linear ticket is substantively discussed in conversation, persist a compressed summary of the discussion as a `CLAUDE.md` document attached to that issue. This builds cumulative context across sessions.

### How it works

1. **Detection** — When the conversation involves a specific ticket (e.g., user mentions "BAL-12", or any workflow targets a ticket), mark that ticket as a logging target for this session.

2. **Check for existing CLAUDE.md** — Before writing, search for a document titled `[TICKET-ID] CLAUDE.md` attached to the issue (use `list_documents` or equivalent filtered by issue).
   - If it exists → read its current content so you can append.
   - If it doesn't exist → you'll create it.

3. **Compress the conversation** — Don't dump raw chat. Summarize what was discussed, decided, discovered, or changed regarding this ticket. Format:

   ```markdown
   ## YYYY-MM-DD

   - **Context:** [Why the ticket came up — what the user was doing/asking]
   - **Discussion:** [Key points, questions asked, answers given — compressed]
   - **Decisions/Outcomes:** [What was decided, what actions were taken]
   - **Open threads:** [Anything unresolved that might resume later]
   ```

4. **Write timing** — Log at the end of the conversation segment about that ticket (when the user moves to a different topic, or the conversation ends). Don't interrupt workflow to log.

5. **Create or append:**
   - **New:** `create_document` with title `[TICKET-ID] CLAUDE.md`, attached via `issue: "TICKET-ID"`. Start with a header: `# CLAUDE.md — [TICKET-ID]` followed by the first entry.
   - **Existing:** `update_document` — append the new dated entry below existing content.

### Confirmation

- **First time per ticket:** Ask once: "Log this conversation to CLAUDE.md on [TICKET-ID]?" On yes, proceed. On no, skip logging for this ticket this session.
- **Subsequent appends in same session:** No re-confirmation needed — the user already approved logging for this ticket.
- **Across sessions:** Always ask on first log attempt per session (the user may not want every conversation logged).

### What NOT to log

- Casual mentions of a ticket with no substantive discussion
- Purely mechanical operations (just changing a label, no discussion)
- Content that's already captured in a Linear document via ticket execution workflow (don't double-log)

### Example

User discusses BAL-12 implementation approach, asks about CUDA Graph patterns, decides on a sub-ticket structure. At end of that segment:

```markdown
# CLAUDE.md — BAL-12

## 2026-04-21

- **Context:** User planning implementation structure for CUDA Graphs blog post
- **Discussion:** Explored sub-ticket breakdown — example scripts, benchmarks, profiler analysis. Discussed PyTorch CUDA Graph API patterns from official docs.
- **Decisions/Outcomes:** Created BAL-23 (basic example), BAL-24 (benchmark), BAL-25 (profiler). Implementation plan document attached to BAL-23.
- **Open threads:** Actual script implementation not yet started. Need to verify CUDA Graph compatibility with PyTorch 2.x dynamic shapes.
```

---
 
## Things to avoid
 
- **Don't over-trigger on casual Linear mentions.** If the user is venting about Linear or mentioning a ticket in passing without asking for workflow action, stay out. The trigger bar is "is there an actual workflow the user is asking me to run?", not "did someone say the word 'ticket'".
- **Don't invent labels, priorities, or statuses.** Always use the real workspace taxonomy — fetch it via `list_issue_labels` / `list_issue_statuses` when needed.
- **Don't batch writes.** One ticket at a time, explicit yes, then move on. This is a hard rule from the user.
- **Don't produce dashboards.** Prose-first outputs. No tables unless the data is genuinely tabular and short.
- **Don't duplicate across workflows.** Sprint planning has a *personal* recap; retrospective has *team-facing* talking points. Keep them distinct.
- **Don't close or delete tickets without explicit confirmation** for that specific ticket.
- **Never move a ticket to Done on your own.** This is the single most important write-boundary. Even after finishing execution work, the ticket stays in its current status unless the user explicitly asks for the Done transition with language that clearly names it ("mark it done", "close ENG-142", "move it to Done"). Generic approvals don't count. When in doubt, ask. See the Confirmation Model section.
- **In ticket execution, don't attach the document to the project.** Always pass `issue:` to `create_document`, never `project:`. The writeup belongs to the specific ticket, not to the project at large.
- **In ticket execution, don't skip the document + comment step.** The work isn't finished until there's a Linear document attached to the issue and a comment linking it — that's the whole point of this workflow.

---

## Examples

Concrete input/output examples live in the `examples/` directory alongside this file. These fix the expected format for each workflow and serve as the ground truth for reproducibility.

| File | Workflow | Description |
|------|----------|-------------|
| `examples/standup.md` | Standup | Daily "what's on my plate" summary with focus recommendation |
| `examples/ticket-execution-research.md` | Ticket execution | Research/analysis task → Linear document + comment (BAL-11 style) |
| `examples/ticket-execution-writing.md` | Ticket execution | Writing/report task → Linear document + comment (BAL-7 style) |

When executing a workflow, follow the output format shown in the matching example. The examples define:
- **Input patterns** — what user phrases trigger the workflow
- **Step sequence** — prerequisite resolution, data gathering, work, drafting, confirmation
- **Output shape** — exact section structure, line format, confirmation prompts
- **Write boundaries** — what requires user approval before writing to Linear
 