# Thesis Scaffold

One unifying outline for the whole thesis: chapter → section → content-block, with
each block marked **written** (drafted in a `chapterN-*/README.md`) or **stub**
(placeholder awaiting content or the researcher's input). This is the master map;
the per-chapter `README.md` files hold the prose.

Legend: ✍️ written · ▫️ stub · 📊 backed by measured data (`SOURCES.md` §6)

---

## Front matter
- ▫️ Title page, abstract
- ✍️ **Attribution & Contributions Statement** (source: `docs/DEVELOPMENT_HISTORY.md`)
- ▫️ Acknowledgements, ToC, lists of figures/tables

## Ch. 1 — Introduction (`chapter1-introduction/`) — ✍️
1.1 Motivation ✍️ · 1.2 Problem & gap ✍️ · 1.3 RQs & hypotheses H1–H5 ✍️ ·
1.4 Contributions ✍️ · 1.5 Scope & honesty ✍️ · 1.6 Roadmap ✍️

## Ch. 2 — Literature Review (`chapter2-literature-review/`) — ▫️ **needs citation set**
2.1 SSI & W3C DID/VC ▫️ · 2.2 Blockchain identity standards (the 9) ▫️ ·
2.3 Vehicle identity & MOBI VID ▫️ · 2.4 V2X security & PKI (IEEE 1609.2 / SAE J2735) ▫️ ·
2.5 Gap this thesis fills ▫️
> Blocked on the researcher's reference set; every claim will cite `SOURCES.md`.

## Ch. 3 — Methodology (`chapter3-methodology/`) — ✍️
3.1 Research design ✍️ · 3.2 Identical-operation-set comparison ✍️ ·
3.3 Gas method + N=30 determinism ✍️📊 · 3.4 V2V method (cold/warm, N=30, CIs) ✍️📊 ·
3.5 Security two-lens method ✍️ · 3.6 W3C executable-checker method ✍️ ·
3.7 MOBI VID multi-backend method ✍️ · 3.8 Threats to validity ✍️

## Ch. 4 — Implementation (`chapter4-implementation/`) — ✍️
4.1 Architecture ✍️ · 4.2 Blockchain identity layer (9 standards) ✍️ ·
4.3 W3C SSI layer (DID/VC/MOBI VID) ✍️ · 4.4 CV2X testbed ✍️ ·
4.5 Comparison & validation framework ✍️ · 4.6 Testing & reproducibility ✍️

## Ch. 5 — Results (`chapter5-results/`) — ✍️📊
5.1 Setup 📊 · 5.2 RQ1 gas (H1) 📊 · 5.3 CVIN-Combined (H5) 📊 ·
5.3.1 H4 multi-backend 📊 · 5.4 RQ4 V2V (H3) 📊 · 5.5 RQ3 compliance (H2) 📊 ·
5.6 RQ2 security 📊 · 5.7 Hypotheses summary 📊 · 5.8 Threats 📊

## Ch. 6 — Discussion (`chapter6-discussion/`) — ✍️
6.1 Security/performance/fidelity frontier ✍️ · 6.2 Which-standard-when ✍️ ·
6.3 V2V viability ✍️ · 6.4 W3C interoperability ✍️ · 6.5 CVIN-Combined ✍️ ·
6.6 Industry & threats ✍️ · 6.7 Summary ✍️

## Ch. 7 — Conclusion (`chapter7-conclusion/`) — ✍️
7.1 Summary ✍️ · 7.2 RQ answers ✍️ · 7.3 Hypothesis verdicts ✍️ ·
7.4 Contributions ✍️ · 7.5 Limitations ✍️ · 7.6 Future work ✍️ · 7.7 Closing ✍️

## Appendices (`appendices/`) — ▫️
A: Gas tables (from `gas_comparison.tex`) · B: Security matrices ·
C: V2V latency stats · D: Contract inventory · E: Reproduction commands ·
F: Source register (`SOURCES.md`)

---

**Status:** 6/7 chapters drafted; Chapter 2 is the one gap (citation set needed).
Chapters 3–7 and §5.* are grounded in the measured artifacts in `SOURCES.md` §6.
