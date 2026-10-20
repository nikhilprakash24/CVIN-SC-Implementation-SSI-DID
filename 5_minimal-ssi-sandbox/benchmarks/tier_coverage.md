# Per-tier function coverage (generated from traces)

| Scenario | Tier | Runs (options) | F-tags covered (/12) | Other tags | tx / view / off-chain entries per run (avg) | Read-only tags on the critical path |
|---|---|---|---|---|---|---|
| batch_anchor | High | 1 (1) | F1 F5 (2) | B1 B2 B3 | 17.0 / 3.0 / 4.0 | B2 |
| bbs_presentation | Medium | 1 (1) | F1 F5 F6 F7 F8 F9 (6) | G0 G1 G2 | 15.0 / 4.0 / 9.0 | F6 |
| delayed_write | Medium (offline) | 1 (1) | F1 F5 F6 F7 (4) | B1 B2 G0 G1 G2 | 10.0 / 4.0 / 12.0 | B2 F6 |
| fl_round | High | 1 (1) | F1 (1) | B1 C1 C2 C3 C4 G0 G1 G2 | 80.0 / 4.0 / 10.0 | C2 C4 |
| i2i | Low (anchors off-chain) | 9 (8) | F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 (12) | — | 13.0 / 6.0 / 1.0 | F12 F2 F6 |
| idpp_port | Cross (High) | 2 (2) | F1 F3 F4 F5 F6 F11 (6) | P1 | 11.0 / 10.0 / 2.0 | F6 P1 |
| s2_dualmode | Low + Medium | 9 (8) | F1 F2 F4 F5 F6 F7 F8 F11 F12 (9) | — | 16.0 / 5.0 / 3.0 | F12 F2 F6 |
| s3_evcharging | Medium | 9 (8) | F1 F5 F6 F8 (4) | G0 G1 G2 | 17.0 / 2.0 / 3.0 | F6 |
| s4_insurance | High | 9 (8) | F1 F2 F3 F5 F6 F7 F9 F10 F11 F12 (10) | G0 G1 G2 | 28.0 / 6.0 / 1.0 | F12 F2 F6 |
| vid_lifecycle | High | 9 (8) | F1 F2 F4 F5 F6 F7 F8 (7) | G0 G1 G2 G4 | 47.0 / 6.0 / 14.0 | F2 F6 G4 |
| vid_minimal | High (issuance) / Medium (verification) | 9 (8) | F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 (12) | G0 G1 G2 G3 G4 T1 T2 | 27.0 / 18.0 / 9.0 | F12 F2 F6 G4 T2 |
| zk_age_gate | Medium | 1 (1) | F1 F5 F8 (3) | Z1 Z2 | 7.0 / 1.0 / 7.0 | Z2 |

Reading: at Low/Medium tiers the critical path carries only view/off-chain entries (F2, F6, F12, G4, T2 reads and off-chain verification); every tx is Tier 3 or asynchronous. Tier 1 (BSM stream in s2_dualmode) has zero chain entries by construction.
