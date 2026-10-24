# Large-Command Protocol — one page

**When to use:** a request that asks for more than one deliverable, more than one document's worth of output, mixes reading a large corpus with writing, or needs iteration (draft → check → correct). Signals: "and then", "also", three or more nouns that are each a document, "with figures and math and commentary", or anything that would need two context windows.

**Why it matters:** a model works best when one session has one job, all its inputs are in front of it, and it knows exactly what to hand forward. A single giant instruction forces it to hold intent, corpus, and output in the same window, and the last third of the work degrades or truncates silently. Splitting is not overhead; it is where the quality comes from.

---

## The loop (five steps, repeat as needed)

**1. Decompose before doing.** Ask for the plan first, not the work: "split this into N prompts, each fitting one session, and show me the set." Approve or edit the set. Cost: one short turn. Benefit: you see the whole shape before any window is spent.

**2. Fix the shared vocabulary once.** Tag namespaces, file-naming pattern, layer/section identifiers, spelling standard, notation rules. Put them in the prompt set so every session uses the same keys. A later session never redefines a tag; it cites it and, if it must change it, logs the correction under a correction key.

**3. Order by dependency, integration first.** Write the index/scan/map before the big narrative, so the narrative is written against a map instead of producing one afterwards. Proofs and numbers go last, because they need the qualitative structure to know what to bound. Meta-commentary is always the final item of a pass.

**4. Carry state with a HANDOFF block, not with memory.** Every session ends by emitting ≤400 words: files issued (exact names), tag ranges consumed, the five load-bearing decisions, open questions, corrections. The next session begins by pasting that block. This is the only mechanism that reliably preserves context across sessions; project search helps but is not a substitute.

**5. Name the cut order in advance.** Each prompt states what to drop first if it runs out of room. If a session still truncates, reply **"continue from ⟦last tag written⟧"** plus the same HANDOFF block. Never re-issue the whole prompt — it re-spends the window on re-reading.

---

## Prompt anatomy (what each session-prompt contains)

| Slot | Content |
|---|---|
| Header | Programme, thread ID, "Prompt k of N" |
| Carry | Pasted HANDOFF from previous session (none for k=1) |
| Inputs | Exact files to read fully vs. to sample by search, in order |
| Task | Numbered sub-tasks with structure specified (sections, tables, figures) |
| Tags | Which namespaces this session may assign and the ranges already consumed |
| Constraints | Spelling, notation, "no bare values", what NOT to write (e.g. numbers in the qualitative doc) |
| Cut order | What to drop first |
| Outputs | Exact file names; "present all"; "end with HANDOFF" |

## Iteration pattern (draft → blind check → diff)

For anything with definitions or derivations: first pass writes freely with its own symbols. Second pass, in a fresh session, receives only the symbol table and the statement of what is to be derived — not the prior derivation — and re-derives. Diff the two. Discrepancies become logged corrections. This catches the error a single session cannot see in itself.

## Rules of thumb

- One session, one job, one HANDOFF.
- Qualitative structure before quantitative bounds; both before commentary.
- Every "X is secured by Y" or "X = value" carries a tag so a later document can cite instead of restate.
- If you change one variable later (a different chain, a different curve), you should be able to cite one tag and move on. Design the tags for that.
- When you are switching topics mid-thread, open a new session with a HANDOFF rather than steering the current one; the current one is carrying state you will lose.
- Ask for the prompt set even when you think the task is medium-sized. If the model returns one prompt, it was fine; if it returns three, you just saved a window.
