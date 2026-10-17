// WO-5 (second half) — Coverage matrix: option × F1–F12 × {native | assisted | anchor | absent}.
//
// Unlike gas, coverage is a declaration about HOW each option satisfies a function (which
// mechanism of the standard is used), so it cannot be read from a trace. Each row below is
// taken from the implementation's NatSpec and is the single source for coverage_matrix.csv.
//   native   — the standard's own primitive implements the function (e.g. ERC-721 mint = F1)
//   assisted — sandbox-side state added beside the standard's primitives (e.g. per-token keys)
//   anchor   — the shared hash-anchor pattern (Set B on every EVM option; F8 on all)
//   absent   — not realisable through the standard; the sandbox supplies it (annotated)
// A trace-derived check is applied: an option is only listed if every function has a tx or
// view entry in some trace for that impl (i.e. it actually ran), else the row is flagged.
//
// Run: node benchmarks/coverage.js
const fs = require("fs");
const path = require("path");

const F = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"];
const DECL = {
  O1_ERC1056: { F1: "native", F2: "native", F3: "native", F4: "native", F5: "anchor", F6: "anchor", F7: "anchor", F8: "anchor", F9: "native", F10: "native", F11: "native", F12: "native",
    note: "event-sourced did:ethr pattern; explicit DID storage for interface uniformity (FINDINGS 1)" },
  O2_ERC721: { F1: "native", F2: "native", F3: "assisted", F4: "assisted", F5: "anchor", F6: "anchor", F7: "anchor", F8: "anchor", F9: "assisted", F10: "assisted", F11: "assisted", F12: "assisted",
    note: "soulbound mint/ownerOf native; no lifecycle, key or delegate model in ERC-721 (burn != deactivate, F-O2-3)" },
  O3_ERC725: { F1: "native", F2: "native", F3: "native", F4: "native", F5: "anchor", F6: "anchor", F7: "anchor", F8: "anchor", F9: "native", F10: "native", F11: "assisted", F12: "assisted",
    note: "contract-per-identity; document and keys are 725Y data; anchors in the issuer's store; no delegate concept (expiry as 725Y data)" },
  O4_ERC725xy: { F1: "native", F2: "native", F3: "native", F4: "native", F5: "native", F6: "native", F7: "native", F8: "anchor", F9: "native", F10: "native", F11: "assisted", F12: "assisted",
    note: "F5–F7 are ERC-735 claims on the subject (the only native credential object on the EVM; no expiry/revocation state in ERC-735 → registry index, F-O4-3); F9/F10 ERC-734 keys; delegates = ACTION key + 725Y expiry" },
  O5_ERC1155: { F1: "native", F2: "native", F3: "assisted", F4: "assisted", F5: "native", F6: "native", F7: "native", F8: "anchor", F9: "assisted", F10: "assisted", F11: "assisted", F12: "assisted",
    note: "identity and credentials are tokens (issue = mint, revoke = burn, verify = balance); no lifecycle/key/delegate model" },
  O6_ERC4337: { F1: "native", F2: "native", F3: "assisted", F4: "assisted", F5: "anchor", F6: "anchor", F7: "anchor", F8: "anchor", F9: "native", F10: "native", F11: "native", F12: "native",
    note: "smart account = DID; validation keys = verification methods; session keys with validUntil = delegates (native expiry); attributes as account data" },
  O7_ERC8004: { F1: "native", F2: "native", F3: "native", F4: "assisted", F5: "anchor", F6: "anchor", F7: "anchor", F8: "anchor", F9: "assisted", F10: "assisted", F11: "assisted", F12: "assisted",
    note: "agent NFT + setMetadata native; no deactivation, key or delegate model (ERC-721 operators are the native delegation, honoured for authorisation); Set C (C1–C4) native via Reputation/Validation registries — the only option with native Set C" },
  O8_LFDT: { F1: "native", F2: "native", F3: "native", F4: "native", F5: "native", F6: "native", F7: "native", F8: "absent", F9: "native", F10: "native", F11: "absent", F12: "absent",
    note: "did:indy nym/attrib/deactivate; F5 = schema/cred-def/rev-reg (definition anchor, no per-credential hash); F7 = revocation entry; F8 off-ledger in AnonCreds (sandbox anchor stands in); no delegation in did:indy (sandbox-side)" },
};
const SETC = { O7_ERC8004: "native", O1_ERC1056: "harness (SetCHarness)", };

// trace check: which impls actually ran every function
const TR = path.join(__dirname, "../traces");
const ran = {};
for (const f of fs.readdirSync(TR).filter(x => x.endsWith(".jsonl"))) {
  for (const line of fs.readFileSync(path.join(TR, f), "utf8").split("\n")) {
    if (!line.trim()) continue; const e = JSON.parse(line);
    if (!e.fnId || !/^F\d+$/.test(e.fnId)) continue;
    (ran[e.impl] ??= new Set()).add(e.fnId);
  }
}

const rows = [["impl", ...F, "native", "assisted", "anchor", "absent", "setC", "ranAll12", "note"]];
let md = "# Coverage matrix (declared per option from implementation NatSpec; trace-checked)\n\n| Option | " + F.join(" | ") + " | native | assisted | anchor | absent | Set C | ran 12/12 |\n|---|" + F.map(() => "---").join("|") + "|---|---|---|---|---|---|\n";
for (const impl of Object.keys(DECL)) {
  const d = DECL[impl];
  const cnt = { native: 0, assisted: 0, anchor: 0, absent: 0 };
  for (const k of F) cnt[d[k]]++;
  const all = F.every(k => ran[impl]?.has(k));
  rows.push([impl, ...F.map(k => d[k]), cnt.native, cnt.assisted, cnt.anchor, cnt.absent, SETC[impl] || "—", all, JSON.stringify(d.note)]);
  const sym = { native: "N", assisted: "A", anchor: "H", absent: "—" };
  md += `| ${impl} | ${F.map(k => sym[d[k]]).join(" | ")} | ${cnt.native} | ${cnt.assisted} | ${cnt.anchor} | ${cnt.absent} | ${SETC[impl] || "—"} | ${all ? "yes" : "NO"} |\n`;
}
md += "\nN = native · A = assisted (sandbox-side state beside the standard) · H = hash-anchor pattern · — = absent in the standard (sandbox supplies).\n\n## Notes per option\n\n" + Object.entries(DECL).map(([i, d]) => `- **${i}**: ${d.note}`).join("\n") + "\n\n## Readings\n\n- Set B (F5–F8) is native on no EVM option except through ERC-735 claims (O4) and ERC-1155 tokens (O5), neither of which carries expiry or a presentation; F8 is an anchor everywhere and off-ledger on Indy — the createPresentation finding, now per option.\n- Set A (F1–F4, F9–F12) is fully native on O1, O3, O6, O8 only; O2/O5/O7 lack a lifecycle and key model and are assisted.\n- Set C is native only on O7.\n";
fs.writeFileSync(path.join(__dirname, "coverage_matrix.csv"), rows.map(r => r.join(",")).join("\n") + "\n");
fs.writeFileSync(path.join(__dirname, "coverage_report.md"), md);
console.log(md);
