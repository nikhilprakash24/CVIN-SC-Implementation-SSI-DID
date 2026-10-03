### L2 — MOBI VID lifecycle gas per event

| Event | ERC-1056 | ERC-721 | ERC-725 | ERC-735 | ERC-1155 | ERC-725xy | LSP8 | ERC-4337 | CVIN-Combined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. VID-I birth certificate | 366,870 | 565,262 | 1,496,416 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 2. Issuer key anchor | 72,243 | 419,990 | 136,952 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 3. Registration credential anchored | 33,918 | 142,897 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 4. Insurance credential anchored | 33,918 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 5. Service endpoint published | 35,012 | 102,961 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 6. Service record 1 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 7. Service record 2 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 8. Service record 3 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 9. Service record 4 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 10. Service record 5 | 35,542 | 125,677 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 11. Delegate key added (k1) | 55,131 | 48,314 | 119,852 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 12. Key rotation (k1 to k2) | 87,987 | 31,214 | 192,830 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 13. Ownership transfer (resale) | 51,742 | 177,562 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 14. Re-registration credential | 33,918 | 125,797 | 119,996 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 15. Credential revocation (old insurance) | 33,470 | 125,809 | 49,218 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 16. Second ownership transfer | 34,646 | 179,574 | 28,390 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| 17. End-of-life deactivation | 34,222 | 27,677 | 23,091 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| **Lifetime total** | 1,050,787 | 2,701,239 | 3,155,103 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Shared deploy gas | 2,709,021 | 2,721,476 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Per-identity deploy gas (in total) | 0 | 0 | 519,384 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 | 3,759,808 | 5,422,715 | 3,674,487 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 | 1,053,496 | 2,703,960 | 3,155,622 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |
| Lifetime + shared/1 000 000 | 1,050,790 | 2,701,242 | 3,155,104 | not impl. | not impl. | not impl. | not impl. | not impl. | not impl. |

_Run 2026-10-03T23-23-59Z_59405ff · commit 59405ff · solc 0.8.24 target cancun runs=200 viaIR=true · Hardhat in-process automine, executes osaka · N=30_
