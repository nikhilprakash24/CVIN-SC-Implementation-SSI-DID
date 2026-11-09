# CVIN-SC · Supervisor Update, Research Side — Panel Note, Reconciliation with the Code Side, and Roadmap

**Document ID:** `CVIN_SC_SupUpdate_ResearchSide_Panel_Note_and_Reconciliation_G-SU1_v0-2` · **Thread:** G-SU1 (supervisor update, research side) · **Version:** v0.2 (second pass; the v0.1 findings are folded into §1) · **Date:** 2026-11-05
**Companions (chat + repo folder `docs/outreach/2026-11-05_supervisor-update_research-side/`, not filed — knowledge cap):** `01_THESIS_ON_ONE_PAGE.md` · `02_THE_WORK_SO_FAR.md` · `03_THE_RESEARCH_PROGRAMME.md` · `04_EMAIL.md` · `05_INTEGRATION_MAP.html` · `README.md` · `figures/research-side-map.png` · PDF and DOCX exports; `_passes/v0-1/` and `_passes/v0-2/` under versioned names `CVIN_SC_SupUpdate_<nn>_<Title>_ResearchSide_G-SU1_v0-<n>`.
**Counterpart:** the code-side folder `docs/outreach/2026-11-05_supervisor-update/` on branch `claude/cool-dirac-uavun2` of `nikhilprakash24/CVIN-SC-Implementation-SSI-DID` (commit `e2ab746`).
**Purpose:** the panel's reading of the research-side pass, the one reconciliation it forces with the code side, what it says to solidify, and what must happen before either side's documents reach the supervisors.

```
Research-side update (G-SU1)   [████████████████░░░░]  v0-2 — six deliverables, two passes, 12 deltas, PDFs built
Both sides to one picture       [████████░░░░░░░░░░░░]  D-R9 ruled; one-pager join written; migration steps 2–10 not started
AI-use agreement (R-0)          [░░░░░░░░░░░░░░░░░░░░]  brief not yet drafted in the candidate's words; not sent
```

---

## 0. The finding the panel leads with

The code-side folder presents the **spoke** as the thesis: title *Comparative Analysis of Self-Sovereign Identity Systems for Connected and Autonomous Vehicles*, five questions RQ1–RQ5, six hypotheses, seven chapters, ≈45,000 words. The hub repository ruled on **30 October 2026 (D-R9)** that the spoke is frozen and absorbed: one unified seven-chapter thesis on the hub spine (`IMinimalSSI` derivation → inventory → evaluation → agents), hub RQ1–RQ3 principal, the spoke's questions as sub-questions, the applied system as Chapter 6, H1–H6 kept only as the spoke's reported expectations, the two lineages' gas never in one table. The code-side documents do not mention D-R9, the hub, `IMinimalSSI`, or the research questions the hub thesis asks; they name the research side only as "not included".

Sent alone, the code-side package tells the supervisors that the thesis is a nine-standard benchmark. The research-side package, written alone, would tell them it is a derived specification. **Neither is the thesis; the ruling is.** So the research-side one-pager was written as the other half of one picture: it carries the hub's questions and status words, the unified chapter table, and a join table mapping every code-side question and hypothesis to its place under RQ2, RQ3 and the cross-cutting feasibility question. The email (04) exists in two variants depending on whether the code-side email has already gone; both carry the join and both carry the disclosure in §0.1.

### 0.1 The second finding: the AI-use gate

G-SD1 §0.1 (verified against UBC G+PS on 2026-11-01) records that substantive generative-AI use must be disclosed and approved in writing **before drafts — including drafts submitted to advisors — are relied on**, and that literal AI output must not appear in drafts shown to advisors without citation. The code-side documents are agent-drafted (their README says so by their working method), and 04 of the code side says nothing about it. Rule R-0 of G-SD1 says no chapter is shown before the brief; the "Thesis on One Page" is not a chapter, but the risk the rule guards against — a supervisor who has seen other students misuse AI reading undifferentiated prose with suspicion — is the same. The research-side 01 therefore carries the disclosure as decision 4; the email carries it in both variants; and if the code-side email has gone, Variant B asks that it be treated as covered. **The one-page brief itself (G-SD1 Stage 1) is still to be drafted in the candidate's own words — that is the first item on the roadmap, ahead of any further document.**

## 1. Pass log (v0.1 → v0.2)

Twelve deltas, logged in the folder README with lens, finding, fix and location. The three that change meaning: **D-01** (methods) — v0.1 said the eleven pre-registration runs were "disclosed by a dated note"; the §2.5 v1-1 note discloses only the eight-option deviation, and the eleven are identified (FIND-R4) but not yet listed — reworded on both documents and added to the integration map as an open item on both sides; **D-02** (identity external) — a precedence claim for the January memos was removed and replaced by the project-listing date with the rule that precedence is claimed only from dated artefacts; **D-03** (writer) — the spoke's word count was carried with both bases (45,000 by the code side's count; 38,900 incl. notes at the text of record) and the hub's 60,200 stated as prose-only. The remaining nine are counts, labels and wording (thirteen hub doc categories, not twelve; "numbered to K-28"; registry v11.3 → v12.0 → v13.1; the June O1 measurement re-run under a pin; figure arrows; terminology). Keep-out sweep passed.

## 2. Panel review — field by field

**CAV / V2X (Michelson lens).** The research-side page says what the vehicular argument claims (the tier *assignment*, the K-15 correction, the Tier-2 read-only path as illustration) and what it does not (Tier 1, measured latency). The join table puts the spoke's V2V result where it belongs — a cross-cutting feasibility question scoped to the verification step — rather than under the hub's RQ labels. *Solidify:* the join table verbatim into Ch. 1 §1.3 of the unified thesis. *Hold:* any sentence that lets the spoke's 0.142 ms stand beside the hub's load-harness floor as if they measured the same thing. *Risk:* a measurement-heavy reader will see the hub's "eight options, declared coverage classes, no rubric verdict" beside the spoke's "563 tests, N = 30, σ = 0" and ask why the thesis leads with the former; decision 2 on the page is the honest place to take that question.

**Blockchain / DLT (Feng lens).** The research-side page is the only document in either folder that states the thesis's formal claim at the strength it has (sufficient and irredundant cover; closure with falsification condition; the three-way `createPresentation` separation). *Solidify:* 02 items 1–4 and 7 as the opening of Ch. 3 and Ch. 5; the numbers-of-record rule (C.4) stated in 01's last paragraph. *Hold:* the spoke's 52,594 "ERC-1056 create" anywhere near the hub's 178,935 / 0 — three values for one phrase is the examiner's first question. *Risk:* "eleven of twelve reproduce to the digit" and "128/128 cells identical" are the two cleanest numbers in the thesis and are easy to over-read as N = 5 everywhere; the status words must travel with them.

**Identity / interdisciplinary (external examiner lens).** The removal of the January-memo precedence sentence (D-02) was necessary; the Atlas's own rule is to cite precedence by repository commit dates. *Solidify:* the "three claims that fail independently" paragraph (02 item 4). *Hold:* the ERC census as anything but provisional until a second rater and a date exist. *Risk:* the agentic generalisation is now constructive on the spoke side (the Steward) and analytic on the hub side; the join (RQ3a) is right, but the R-1 scope amendment of 30 October must be visible in the methodology chapter or the examiner reads the Steward as scope creep.

**Research methods.** Both passes kept the pre-registration honest: pre-registered 15 October; eight-option deviation disclosed; eleven earlier runs identified and *not yet listed*. *Solidify:* the §2.5 amendment as the next research-side writing act — 200 words, dated. *Hold:* "admitted" and "verdict" as distinct words; D-R7 admits, D-R8 measures. *Risk:* the code-side README's "every number verified against its primary file" and the research side's "every number from a filed document of record" are both true and both sides still carry stale sentences in their own governance files (the code-side README lists them; the hub's `STATUS.md` has the "still unpushed" line); say so once, in the preface, rather than letting an examiner find both.

**Software / systems.** The folder mirrors the code side's layout file for file, with `_passes/` holding both versions under versioned names, so the two folders can sit side by side on one branch. *Solidify:* one outreach directory per side, same six files, same README table. *Hold:* nothing. *Risk:* the research-side folder is not yet on any remote; the code-side one is. Push to the same branch or a sibling, then the README links resolve.

**Professional ECE researcher.** The research-side page answers the question an engineering examiner asks first — *what is the result and how strong is it* — in one table with a status column. The code-side page answers *what was built and measured*. Together they are the abstract and the evidence; apart they are two theses. *Solidify:* the two one-pagers as the first two pages of the supervisor package, in that order (research side first, because it states the spine).

**Professional technical writer.** The one-pager runs to five PDF pages; the code side's "one page" is the same shape, so the name is a genre, not a length. Each 02/03 pair reads as a counterpart (same headings, same tables, "this side" / "that side"), which is the point. *Solidify:* the shared heading structure. *Cut, later:* 03's lane table and 05's lane table overlap by half; one should point at the other once the folder is on a branch.

**Academic-integrity chair (added for this lane).** The disclosure is in the email and on the page, but the brief that UBC's guidance actually wants — one page, first person, use to date and approval going forward, with the timeline attached — does not yet exist in the candidate's words. Until it does, the candidate is sending AI-assisted documents that *announce* a disclosure rather than *make* one. *Solidify:* G-SD1 Stage 1 next, before any further outreach document. *Hold:* the word "legitimate" out of everything; the evidence does the arguing.

**Programme manager.** This pass cost one sitting and produced the research side's half of the supervisor picture; the panel's two findings (§0) were available for the price of reading `STATUS.md` and G-SD1 §0.1 against the code-side folder. The knowledge store is at 1.92 of 2.00 MB; only this note is filed. The folder goes to the repository.

## 3. Ranked — what to solidify from this pass

| Rank | Item | Why |
|---|---|---|
| 1 | The join table (01, last section) — spoke RQ/H → hub RQ2a–d, RQ-V, RQ-V2, RQ3a | it is D-R9 made legible; without it the supervisors hold two theses |
| 2 | The AI-use disclosure as decision 4 and in both email variants — then the brief itself (G-SD1 Stage 1) | UBC gate; protects every document sent so far |
| 3 | 02 items 1–4, 6, 7 with their status words | the thesis's formal claim and its one verdict, stated once at the right strength |
| 4 | The numbers-of-record rule in one paragraph (01 end; 05 join table) | prevents the three-values-for-one-phrase failure |
| 5 | 04 Variant B's sentence treating already-sent documents as covered | honest, short, and it closes the gate retroactively |
| 6 | 05's research-side decisions board as the only to-do list this week | ten rulings, most one line, most owed by the candidate |
| 7 | 03's "writing as a record of judgement" section (narrowings; the K-15 example; the provenance layer) | it is the research side's answer to "what did the AI do" |
| 8 | The README's corrections table (eleven not nine; 166,664; deployment gas now recorded; 60,200 prose-only; 45,000 vs 38,900) | stops the next session reintroducing superseded figures |
| 9 | The lane-map figure with its three states (filed / chat-only / outside corpus) | the shape of the whole, including what only the author can present |
| 10 | The eleven-run amendment as the next research-side writing act | 200 words that convert a disclosure defect into evidence of discipline |

## 4. Reconciliation ledger — code side ↔ research side

| Topic | Code-side document says | Research side / ruling says | Resolution in this pass |
|---|---|---|---|
| What the thesis is | Spoke: nine standards, RQ1–RQ5, H1–H6, seven chapters | D-R9: one unified thesis on the hub spine; spoke = Ch. 6 + sub-questions | 01 join table; 04 both variants; decision 2 |
| Title | *Comparative Analysis…* with replacement proposed (D-14) | *Towards a Minimal Function Specification…*; "minimal" qualified | decision 5 on both pages, same options |
| Word count | ≈45,000 | ≈38,900 incl. notes at the 31 Oct text of record; hub 60,200 prose; unified ≈68,000 | both bases carried (D-03) |
| Gas | native-analogue gas, N = 30 determinism, viaIR/cancun | protocol gas N = 5, legacy/paris; never mixed | 01 last paragraph; 05 join |
| Test counts | 563 Hardhat + 376 Python | 133 sandbox; 201 is history; never summed | 05 "three things to know" |
| ZK | ZkVinGate 301,163 gas | age-gate admit 250,283; different circuits | README corrections; never compared |
| Steward / RQ5 | adopted as extension (decision 1) | R-1 amendment dated 10-30; RQ3a + RQ-V2 | join table |
| AI assistance | not mentioned | UBC gate; R-0; origin tags | decision 4; 04 A/B; this note §0.1 |
| Known stale values | 1.226× → 1.197×; 0.153 → 0.142 ms; P* 609 → 641; "second-highest" → third | hub `STATUS.md` "still unpushed" line; nine → eleven pre-P runs | both sides list their own; preface sentence recommended |

## 5. Roadmap — what happens before anything else is sent

1. **Draft the AI-use brief in the candidate's words** (G-SD1 Stage 1; the plan's §1.5 is the spec), attach the authorship timeline and contribution map (Stage 2), send (R-0). Record the date and the reply in the G-SD1 meta-log.
2. **Decide 04 A or B** by whether the code-side email has gone; send the research-side PDFs with it.
3. **File D-18** (the 61 unfiled sets) and authorise **R-F4** (D-1) — one hour, and every later programme depends on it.
4. **Write the §2.5 amendment** listing the eleven pre-registration traces by date.
5. **Push the research-side folder** beside the code-side one (same branch or sibling) so both READMEs link.
6. Then the D-R9 migration (steps 2–4 first), Takes 2 and 3, G-SD1 Stages 3–10 on the unified spine.

## 6. Save point

```
SAVE-POINT G-SU1 2026-11-05 · research-side update v0-1 + v0-2 delivered (md · html · png · docx · pdf) ·
folder docs/outreach/2026-11-05_supervisor-update_research-side/ prepared, not yet pushed · this note filed v0-2 ·
next: candidate drafts the AI-use brief (G-SD1 S1), decides 04 A/B, pushes the folder, rules the board · nothing deleted; nothing promoted
```
