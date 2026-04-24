# Ticket Execution Example: Writing / Report

Captured from Apr 19, 2026 session. User asks to produce a deliverable document for a ticket.

---

## User Input

```
BAL-7 콘클라베 감상 보고서 작성해줘
```

(Alternative triggers: "write the report for BAL-7", "work on BAL-7", "handle this ticket")

---

## Step 1: Fetch the ticket (silent)

`get_issue` on BAL-7. Extract:
- Title: "Assignment: Conclave (2024) 영화 감상 보고서 작성"
- Status: In Progress, Priority: High, Due: 2026-04-29
- Description: acceptance criteria specifying format, length (2,000-4,000 chars), section requirements
- Comments: check for prior work or instructions

---

## Step 2: Confirm scope

```
BAL-7 asks for a Conclave (2024) movie report. The acceptance criteria specify
2,000-4,000 characters with specific section requirements. I'll research the
film and draft the report as a Linear document.

Shall I proceed?
```

User: `yes`

---

## Step 3: Do the work

1. Research the film: plot, characters, themes, critical reception
2. Draft the report following acceptance criteria format
3. Iterate on draft if needed (check character count, section proportions)

---

## Step 4: Present in-chat summary + document draft

### In-chat summary

```
Drafted the Conclave report. It's structured as a trial-format analysis
(prosecution vs. defense for each cardinal's corruption), covering power,
faith, institutional corruption, and identity themes. Total: 2,980 characters
(74.5% of the 4,000 char limit), meeting the 2,000+ minimum.

Here's the full document:
```

### Document draft

```markdown
# [BAL-7] 콘클라베(Conclave, 2024) 감상 보고서

## I. 서론
[Opening section — film overview, thesis statement...]

## II. 줄거리 요약
[Plot summary — key events, conclave process...]

## III. 주요 인물 분석
### 로렌스 추기경 (랄프 파인즈)
[Character analysis with 5 argument points...]

### 테데스코 추기경 (세르지오 카스텔리토)
[Character analysis with 5 argument points...]

## IV. 결론
[Thematic synthesis — power, faith, institutional corruption...]
```

### Proposed comment

```
감상 보고서 작성 완료: [BAL-7] 콘클라베(Conclave, 2024) 감상 보고서.
재판 형식 분석 구조, 총 2,980자. 로렌스 vs 테데스코 변론 중심.
```

### Confirmation prompt

```
Create the document (attached to BAL-7) and post the comment?
```

---

## Step 5: On user approval

1. `create_document` with `issue: "BAL-7"`. Title: "[BAL-7] 콘클라베(Conclave, 2024) 감상 보고서"
2. `save_comment` on BAL-7 with comment text + document link
3. Report back

```
Done:
- Document created: https://linear.app/ball-space/document/bal-7-콘클라베conclave-...
- Comment posted on BAL-7 with link

The ticket stays In Progress. Want to adjust the status?
```

---

## Revision Flow

If the user asks for changes after the document is created:

```
User: 분량을 좀 더 늘려줘 (increase the length)
```

1. `get_document` to fetch current content
2. Revise and show the diff or full updated draft
3. On approval, `update_document` (not create a new one — this is a revision, not a new request)
4. Post updated comment if the changes are significant

---

## Format Rules

- Fetch ticket and check acceptance criteria before drafting
- Match the document structure to the ticket's requirements
- In-chat summary: character count, structure overview, key decisions
- Full document draft shown before creation
- `create_document` with `issue:` parameter
- Revisions use `update_document` on the same document
- New separate requests create new documents
- Never move ticket to Done without explicit user request
