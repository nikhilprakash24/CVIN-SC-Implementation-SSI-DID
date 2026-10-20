

> **SC-02 — partially closed 2026-10-04 (stream G-K, M5).** A bounded on-chain observability analysis for
> pseudonymity was run as pre-registered (PLAN_MOBI_SUMO §A.2): `4_comparison-framework/results/pseudonym_pool.*`,
> register row #38.
>
> - **The 20-delegate pool on the standard ERC-1056 registry is fully linkable.** A passive observer needs one
>   `eth_getLogs` by identity topic. The pool costs ≈1.10 M gas per 5-minute epoch, not the pre-registered ≈1.44 M
>   (gas claim FAIL).
> - **Per-pseudonym `did:ethr` identities are not linkable by that query.** They cost 0 gas while they need no
>   on-chain attribute.
> - **Once an attribute is written,** pseudonyms are re-linked by their funding transactions when self-funded, or
>   share a relayer's anonymity set when relayed. Either way they cost more than the pool.
>
> **Still deferred:** radio/timing/position linkability, group revocation for implicit pseudonyms, and a measured
> SCMS baseline. These stay future work.
