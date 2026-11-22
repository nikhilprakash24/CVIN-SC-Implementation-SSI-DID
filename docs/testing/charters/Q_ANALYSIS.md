# Charter Q — Analysis (derived results)

**Status:** draft, 2026-10-22. **Binds:** guide 1.2.1, 1.2.7; `docs/CVIN-DATA-COLLECTION-FRAMEWORK.md` §6a, §8.

## 1. What a derived result establishes
A pure function of results of record: ratios, the capability matrix, dominance and the Pareto frontier, rubric inputs,
the feature-asymmetry matrix. It adds no measurement; it can be no stronger than its inputs.

## 2. Oracle
Re-derivation: the analysis re-run on the same run directory gives the same output (`npm run metrics:analyze`;
generated documents checked in CI).

## 3. Design
Criteria are declared before the analysis is read. Lower-bound inputs (lifetime totals excluding n/a events, marked
†) are kept out of comparisons that would overstate them, or the comparison says so.

## 4. Falsifiers it carries
| Hypothesis | Refuting observation | Row |
|---|---|---|
| H5 (the hybrid is on the frontier) | the hybrid dominated on the declared criteria — **observed** (#36) | #36 |
| H1 at lifetime level (≥ 10×) | a rich-state option within 10× on lifetime gas — **observed** (#30, #35) | #30, #35 |

## 5. Threats to validity
| Type | Threat | Control |
|---|---|---|
| Construct | **the H5 criteria changed** from the four in the framework's §8 to the six in §6a after the framework was written | to be recorded as a scope change and in a pre-registration amendment (guide 1.2.7); both sets reported |
| Internal | a run-dependent latency axis inside a dominance criterion (#36 note) | dominance reported per criterion set, cost-only first |
| Construct | rubric cells author-scored | rubric JSON's `reviewed` flags; a second scorer is an author decision |

## 6. Reporting
Each derived table names its run of record and its criterion set.

## 7. Replication
Inherits its inputs'.

## 8. Limits
The rubric is scored for few substrates; quantitative rubric inputs come from the harness (A5), qualitative cells
are the author's.
