# Chapter 2 — the six `[SOURCE NEEDED]` markers (plan, written before searching)

**Author:** Nikhil Prakash (MASc, UBC ECE). **Written:** 2026-10-31. **Binds:** `docs/STYLE_AND_RIGOUR_GUIDE.md`
(rule 1.2.2: "checked against", not "compliant", until a clause-level citation exists).

| # | Line (README) | Kind | What a search can settle |
|---|---|---|---|
| S1 | §2.2 multi-standard Ethereum identity benchmark | absence | widen coverage beyond Consensus + Crossref; any counterexample found is cited and the claim narrowed |
| S2 | §2.3 MOBI VID I / VID II specification documents | document | the published spec's title, version and date, if public; otherwise say it is member-only |
| S3 | §2.3 academic evaluation of MOBI VID | absence/source | any paper implementing or evaluating MOBI VID is cited |
| S4 | §2.4.1 SAE J2735 edition and date | document | the current edition's designation and date from SAE's own catalogue |
| S5 | §2.4.4 SSI and PKI verify in one simulated V2V path | absence | as S1 |
| S6 | §2.6 measured custodian / wallet-agent evaluation (vehicle or IoT) | source | any measured evaluation is cited |

**Rules.** A source is cited only after its page or abstract has been read (no citation from a search snippet alone).
An absence claim keeps its marker, reworded to name the databases and queries covered and the date, because the
author's own search is still owed; the coverage goes in `SOURCES.md`. A counterexample changes the claim's wording,
never silently. Searches: Consensus, alphaXiv (arXiv), web (publisher and standards-body pages).

**Done when** each marker is either replaced by a read citation or reworded with its recorded coverage, and the
chapter's checks pass.
