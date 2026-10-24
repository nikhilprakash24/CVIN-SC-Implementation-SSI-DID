#!/usr/bin/env python3
"""Result cards: every verified result of the claim register as one card (report 18, step RC).

    python3 docs/figures/make_result_cards.py          # write docs/figures/result_cards.html
    python3 docs/figures/make_result_cards.py --check  # CI

Reads only committed files: the claim register (`docs/MEASUREMENT_CONDITIONS.md`), the dashboard snapshot
(cruxes) and the gas charter's classes (`docs/testing/gas_charter.py`). The cards' titles and headlines are
written here by hand, because the register's bold text marks emphasis as well as values. The check fails if:
  - a V row has no card, or a card names a row that is not V;
  - a card's headline is not verbatim in its register row;
  - any number in a card's headline, caption or verdict is not in its register row;
  - a verdict says PASS or FAIL and the row does not;
  - the page on disk differs from the page built now.
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/MEASUREMENT_CONDITIONS.md"
SNAPSHOT = ROOT / "docs/figures/dashboard_snapshot.json"
OUT = ROOT / "docs/figures/result_cards.html"
sys.path.insert(0, str(ROOT / "docs/testing"))
from gas_charter import ROWS as GAS_CLASS  # noqa: E402

# Groups, in page order. Every V row is in exactly one.
GROUPS = [
    ("cost", "Identity cost on chain", "Gas to create and change an identity, per standard."),
    ("lifetime", "Lifetime, footprint and frontier", "Cost over a vehicle's life, storage written, and which standards are dominated."),
    ("read", "Reading the chain", "What a verifier pays to read identity state."),
    ("verify", "V2V and V2I verification", "Off-chain verification latency and message size."),
    ("fresh", "Revocation and freshness", "How many messages a cached verifier accepts after a revocation."),
    ("security", "Security", "Attacks injected and how they were refused."),
    ("w3c", "Standards conformance", "W3C DID and VC conformance."),
    ("mobi", "MOBI lifecycle and privacy", "The pre-registered MOBI experiments."),
    ("zk", "Zero-knowledge identity and the agent wrapper", "Layer 5: the ZK-VIN circuit, its costs, and the narrowing attack."),
]

# row: (group, title, headline, caption, verdict or None)
CARDS = {
    1: ("cost", "createVehicleDID", "78,090", "gas, CVIN registry, test-suite context", None),
    2: ("cost", "ERC-1056 changeOwner", "68,854", "gas; addDelegate 72,219, setAttribute 51,126", None),
    3: ("cost", "ERC-721 mint", "102,804", "gas, average over the test suite", None),
    6: ("cost", "ERC-1056 against ERC-721, create", "10.3×", "bare createIdentity against mintVehicle; 6.9× with the VIN bound on both sides. The ratio depends on the operation definition", None),
    22: ("cost", "Testbed registry, issue attribute", "37,807", "gas; 37,783–37,807 from calldata zero bytes; deploy 944,729", None),
    25: ("cost", "Create-identity spread, nine standards", "33.7×", "52,216 gas (CVIN-Combined) to 1,757,881 (ERC-735); EntryPoint indirection +46,830 gas per operation", None),
    29: ("cost", "Harness create, three substrates", "76,830 / 402,567 / 656,480", "C1 gas, ERC-1056 / 721 / 725, mode of the cell's iterations", None),
    34: ("cost", "Heaviest create in the harness", "1,757,881", "ERC-735 C1 gas; ERC-1056 76,830; CVIN-Combined 271,402", None),
    47: ("cost", "RSU key anchor (I4)", "52,582–52,606", "gas over declared seeds 1–30, mode 52,606; creating the RSU identity costs 0", "reported, no verdict"),
    54: ("cost", "Holder-written presentation, ERC-1056 (P1)", "34,206", "gas for createPresentation; unchanged on the merged tree (run 2026-10-21T03-28-59Z_a9e2a28)", None),
    50: ("cost", "Relayed write overhead", "+27,622", "gas: ERC-1056 relayed U5 62,646 against direct U3 35,024; ERC-4337 +47,116", None),
    26: ("lifetime", "Cheapest over a vehicle's life", "1,450,146", "gas, ERC-1056 over 15 years; marginal cost O(1) in history", None),
    30: ("lifetime", "MOBI lifecycle, ERC-1056 cheapest", "2.58× / 3.00×", "17 events: 1,050,809 / 2,706,685 / 3,155,103 gas (ERC-1056 / 721 / 725)", None),
    35: ("lifetime", "Lifecycle, heaviest of nine", "5,797,549", "gas, ERC-735 over 17 events; ERC-1056 1,050,809", None),
    36: ("lifetime", "CVIN-Combined on the frontier", "dominated", "by ERC-4337 on all six declared criteria", None),
    49: ("lifetime", "New storage slots over a lifecycle", "149", "zero→nonzero SSTOREs, ERC-735, 17 events; ERC-1056 8", None),
    42: ("lifetime", "History: 2026-10-04 defect fixes", "+227,534", "gas on the ERC-735 deploy (issuer registry code); pre-merge contracts", None),
    43: ("lifetime", "History: pass-06 fixes", "+491,204", "gas on the ERC-1155 deploy; 10 of 61 nine-standard cells moved", None),
    31: ("read", "Resolution against history", "91.113 ms", "ERC-1056 at h = 50: 112 RPC calls, 87 KB; median, in-process", None),
    51: ("read", "Read cost at h = 50, ERC-1056", "112 / 87033", "RPC calls / bytes for R3; ERC-1155 stays at 3 / 908", None),
    21: ("read", "ERC-1056 verify against PKI", "≈69×", "15.513 ms ERC-1056 uncached against 0.226 ms PKI, median, n=50", None),
    27: ("verify", "V2V SSI verify, warm", "0.142 ms", "95 % CI [0.141, 0.143]; PKI warm 0.090 ms; simulated mobility, real crypto", None),
    23: ("verify", "Signed BSM size, ERC-1056", "596 B", "PKI ≈1.08–1.11 kB, carrying its PEM certificate", None),
    44: ("verify", "SPaT against BSM warm verify (I1)", "1.197", "ratio, 95 % CI [1.193, 1.201]; pass band [0.80, 1.20]; 1.226 on the run of record", "at the edge of the band, not falsified"),
    48: ("verify", "Crypto on the controller to vehicle path (I5)", "0.805 ms", "95 % CI [0.800, 0.817]; the sum of four operations, not a path latency", "reported, no verdict"),
    32: ("fresh", "Freshness knee, full refresh", "k ≈ 90", "for P*(0.5) = 100; at most 0 / 4 / 24 messages accepted after a revocation at k = 1 / 5 / 25", None),
    37: ("fresh", "One-call probe refresh", "3.222 / 3.035 ms", "against 14.136 / 14.751 ms for a full refresh; both modes reach P*(0.5) = 100 on this host", None),
    39: ("cost", "R3 resolve at h = 50 over HTTP-RPC, ERC-1056", "162.5 / 168.2", "median / p95 ms; ERC-1155 4.7 / 5.7 on the merged contracts; gas identical to the in-process run", None),
    52: ("fresh", "#32 against #37 on one host (C3)", "attributed to the host", "full-refresh t_chain 7.57 / 7.91 ms (#32 code) and 6.94 / 8.15 ms (#37 code); here the probe reaches P*(0.5) ≥ 100 at k = 25", "decision rule committed before the runs"),
    55: ("fresh", "Probe refresh on the same host", "5.85 ms", "chain time for one RPC against 18.80 ms for a full refresh (4 RPCs); no knee in either mode", None),
    46: ("fresh", "Revoked RSU in a verifier's cache (I3)", "k − 1", "the most SPaT accepted after revocation: 0, 4, 24 at k = 1, 5, 25, over N=30 runs", "PASS"),
    28: ("security", "Attacks defended", "43/43", "each reverted with its documented reason; attestEvent fixed path 198,694 execution gas since the owner-or-delegate check (WM-2 C2)", None),
    45: ("security", "SPaT attacks rejected (I2)", "30/30", "runs: each of 15 registered checks rejected for its expected reason; 0 legitimate SPaT rejected of 138,895", "PASS"),
    4: ("w3c", "W3C compliance, internal checker", "94.3%", "44 executed checks: 41 PASS, 1 PARTIAL, 2 FAIL; self-scored", None),
    53: ("w3c", "Basic digital-ID set A, full coverage", "11/11", "operations supported by ERC-1056 pure, ERC-725, ERC-4337 and CVIN-Combined; a derivation from the capability flags", None),
    24: ("w3c", "External W3C DID test suite", "335/336", "generated tests; resolution 193/194; not comparable with 336/441", None),
    33: ("mobi", "M4 lifecycle parity", "≈1,850–5,930×", "MOBI writes against the centralized baseline; cached history ratio 0.072", "writes ≥10×: PASS ×3; equal once cached: FAIL"),
    56: ("zk", "ZK-VIN circuit", "3,498 constraints", "1,667 non-linear, 1,831 linear; 3,505 wires; circom 2.2.2", None),
    57: ("zk", "ZK-VIN proof, prove and verify", "prove median 398.6 ms", "verify median 18.42 ms; proof 256 B as calldata; insecure single-party setup", "Z-E1, Z-E2, Z-E4 PASS"),
    58: ("zk", "ZK-VIN admission on chain", "301,163", "gas for admit with on-chain Groth16 verification; anchor 51,558; Schnorr proof of knowledge 28,775", "Z-E3 PASS"),
    59: ("zk", "Sigma-protocol primitives", "exact group-operation counts", "Schnorr, Pedersen, Chaum–Pedersen, OR, range and threshold proofs; pure-Python reference code", None),
    60: ("zk", "Unsalted VIN hash reversed", "3.58 s", "10⁶ candidates at 279,587 hashes/s on one core; extrapolations are estimates", "Z-E7 PASS"),
    61: ("zk", "Twenty-questions attack against the Steward", "≤ 3.0 bits", "adversary leakage on all runs; honest service below 90 % on 25/60 (minimum 70.0 %); undefended: exact within 5 queries", "Z-E5 PASS; Z-E6 FAIL"),
    62: ("zk", "Manual burden of ZK identity", "92,623", "field multiplications to verify one 6-bit threshold proof by hand; counts exact, hand times estimated", None),
    38: ("mobi", "M5 pseudonym pool, per epoch", "1,096,368", "gas for 20 addDelegate per 5-min epoch, 0.76× the pre-registered ≈1.44 M; one query links 60/60 pseudonyms", "gas FAIL; linkability PASS (fully linkable)"),
}

NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def parse_register():
    rows = {}
    for line in REGISTER.read_text().splitlines():
        m = re.match(r"^\| (\d+) \| (.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split(" | ")]
        status_text = " ".join(cells[4:])
        st = re.match(r"\s*\*\*([VESUB])", status_text)
        rows[int(m.group(1))] = {
            "claim": cells[0], "location": cells[1], "tag": cells[2], "source": cells[3],
            "status": st.group(1) if st else "?", "note": status_text,
        }
    return rows


def plain(s):
    return s.replace("**", "").replace("`", "")


def nums(s):
    return {n.replace(",", "") for n in NUM.findall(s)}


def problems_for(rows):
    out = []
    v_rows = {n for n, r in rows.items() if r["status"] == "V"}
    for n in sorted(v_rows - set(CARDS)):
        out.append(f"register row #{n} is V and has no card")
    for n in sorted(set(CARDS) - v_rows):
        out.append(f"card #{n} names a row that is not V")
    groups = {g[0] for g in GROUPS}
    for n, (g, _t, head, cap, verdict) in CARDS.items():
        if n not in rows:
            continue
        text = plain(rows[n]["claim"] + " " + rows[n]["note"])
        if g not in groups:
            out.append(f"card #{n}: unknown group {g}")
        if head not in text:
            out.append(f"card #{n}: headline {head!r} is not verbatim in the row")
        missing = nums(head + " " + cap + " " + (verdict or "")) - nums(text)
        if missing:
            out.append(f"card #{n}: numbers not in the row: {sorted(missing)}")
        for word in ("PASS", "FAIL"):
            if verdict and word in verdict and word not in text:
                out.append(f"card #{n}: verdict says {word}, the row does not")
    return out


def inline(s):
    """Register markdown to safe inline HTML: code spans and bold only."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return s.replace("**", "").replace("`", "")


def short(s, n):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    # do not leave a bold or code span open
    if cut.count("**") % 2:
        cut = cut.rsplit("**", 1)[0]
    if cut.count("`") % 2:
        cut = cut.rsplit("`", 1)[0]
    return cut.rstrip(" ,;(") + " …"


def verdict_state(v):
    if not v:
        return None
    if "FAIL" in v and "PASS" in v:
        return "mixed"
    if "FAIL" in v or "outside" in v:
        return "fail"
    if "PASS" in v:
        return "pass"
    return "none"


def build():
    rows = parse_register()
    problems = problems_for(rows)
    snap = json.loads(SNAPSHOT.read_text())
    crux_of = {}
    for c in snap["cruxes"]:
        for e in c["evidence"]:
            crux_of.setdefault(e["row"], []).append(c["id"])
    crux_title = {c["id"]: c["title"] for c in snap["cruxes"]}
    v_count = sum(1 for r in rows.values() if r["status"] == "V")
    prereg = sum(1 for c in CARDS.values() if c[4])
    by_status = {}
    for r in rows.values():
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    sections = []
    for gid, gtitle, gsub in GROUPS:
        cards = [(n, c) for n, c in CARDS.items() if c[0] == gid and n in rows]
        cards.sort(key=lambda x: x[0])
        items = []
        for n, (_g, title, head, cap, verdict) in cards:
            r = rows[n]
            chips = [f'<span class="chip tag" title="Measurement conditions">{inline(short(r["tag"], 48))}</span>']
            if n in GAS_CLASS:
                chips.append(f'<span class="chip gas" title="Gas class, docs/testing/GAS_CHARTER.md">{GAS_CLASS[n][0]}</span>')
            for cid in crux_of.get(n, []):
                chips.append(f'<span class="chip crux" title="{html.escape(crux_title[cid])}">{cid}</span>')
            vs = verdict_state(verdict)
            vhtml = (f'<p class="verdict" data-v="{vs}"><span class="vk">Verdict</span> {html.escape(verdict)}</p>'
                     if verdict else "")
            search = html.escape(plain(" ".join([title, head, cap, verdict or "", r["claim"], r["tag"]])).lower(), quote=True)
            items.append(
                f'<article class="card" data-group="{gid}" data-pre="{1 if verdict else 0}" data-text="{search}" id="r{n}">'
                f'<div class="top"><a class="rid" href="#r{n}">#{n}</a><span class="st">V</span></div>'
                f'<p class="head">{html.escape(head)}</p>'
                f'<h3>{html.escape(title)}</h3>'
                f'<p class="cap">{html.escape(cap)}</p>'
                f'{vhtml}'
                f'<div class="chips">{"".join(chips)}</div>'
                f'<details><summary>Register row</summary>'
                f'<p class="claim">{inline(short(r["claim"], 520))}</p>'
                f'<dl><dt>Source</dt><dd>{inline(short(r["source"], 260))}</dd>'
                f'<dt>Quoted in</dt><dd>{inline(short(r["location"], 160))}</dd>'
                f'<dt>Status</dt><dd>{inline(short(r["note"], 360))}</dd></dl>'
                f'</details></article>')
        sections.append(
            f'<section class="group" data-group="{gid}"><div class="ghead"><h2>{html.escape(gtitle)}</h2>'
            f'<p>{html.escape(gsub)} <span class="count">{len(items)}</span></p></div>'
            f'<div class="cards">{"".join(items)}</div></section>')

    others = []
    for n in sorted(rows):
        r = rows[n]
        if r["status"] == "V":
            continue
        others.append(f'<li><span class="rid">#{n}</span><span class="chip st-{r["status"]}">{r["status"]}</span>'
                      f'<span class="oc">{inline(short(r["claim"], 150))}</span></li>')

    chips = ['<button type="button" class="f on" data-f="all" aria-pressed="true">All</button>',
             '<button type="button" class="f" data-f="pre" aria-pressed="false">Pre-registered</button>']
    chips += [f'<button type="button" class="f" data-f="{g}" aria-pressed="false">{html.escape(t)}</button>' for g, t, _ in GROUPS]

    page = TEMPLATE
    for k, v in {
        "__VCOUNT__": str(v_count), "__ROWS__": str(len(rows)), "__PREREG__": str(prereg),
        "__GAS__": str(len([n for n in CARDS if n in GAS_CLASS])),
        "__STATUS__": " · ".join(f"{k} {by_status[k]}" for k in "VESUB" if k in by_status),
        "__FILTERS__": "".join(chips), "__SECTIONS__": "".join(sections), "__OTHERS__": "".join(others),
        "__NOTV__": str(len(others)),
    }.items():
        page = page.replace(k, v)
    return page, problems


TEMPLATE = """<title>CVIN Result Cards</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: the results board's palette and faces, as a deck of result cards: one card per verified register row, grouped by question, with a filter row on top. */
:root {
  --bg: #f3f4f2; --panel: #ffffff; --ink: #15191c; --ink-2: #4c555b; --muted: #7d868b; --rule: #dde1df;
  --accent: #c27a00; --accent-soft: #f6e7c8; --good: #217a3c; --warn: #a86400; --crit: #b3261e; --na: #8a9399; --bar: #2f5d73;
  --font-display: "Barlow Semi Condensed", "Arial Narrow", system-ui, sans-serif;
  --font-body: "Barlow", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-data: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #101416; --panel: #171d20; --ink: #e8ecea; --ink-2: #b4bdc1; --muted: #87929a; --rule: #2a3236;
    --accent: #f0a529; --accent-soft: #3a2d14; --good: #5cc27a; --warn: #f0a529; --crit: #ef6b62; --na: #7d878d; --bar: #6aa6c2;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #101416; --panel: #171d20; --ink: #e8ecea; --ink-2: #b4bdc1; --muted: #87929a; --rule: #2a3236;
  --accent: #f0a529; --accent-soft: #3a2d14; --good: #5cc27a; --warn: #f0a529; --crit: #ef6b62; --na: #7d878d; --bar: #6aa6c2;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--font-body); font-size: 15px; line-height: 1.5; }
.wrap { max-width: 1240px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 48px; display: grid; gap: 28px; }
header { display: grid; gap: 8px; border-bottom: 3px solid var(--accent); padding-bottom: 16px; }
.eyebrow { font-family: var(--font-display); font-weight: 600; letter-spacing: .08em; text-transform: uppercase; font-size: 12px; color: var(--accent); }
h1 { font-family: var(--font-display); font-weight: 700; font-size: clamp(28px, 4vw, 40px); line-height: 1.05; margin: 0; text-wrap: balance; }
.lede { color: var(--ink-2); max-width: 72ch; margin: 0; }
.kpis { display: flex; flex-wrap: wrap; gap: 10px 32px; margin-top: 6px; }
.kpi { display: grid; }
.kpi .k { font-family: var(--font-data); font-size: 22px; font-weight: 500; font-variant-numeric: tabular-nums; }
.kpi .l { font-size: 12px; color: var(--ink-2); }
.bar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; position: sticky; top: env(safe-area-inset-top, 0px); z-index: 2; background: var(--bg); padding-block: 10px; border-bottom: 1px solid var(--rule); }
.f { font: 600 13px var(--font-display); letter-spacing: .03em; color: var(--ink-2); background: var(--panel); border: 1px solid var(--rule); border-radius: 999px; padding: 4px 12px; cursor: pointer; }
.f:hover { border-color: var(--ink-2); }
.f.on { background: var(--ink); color: var(--bg); border-color: var(--ink); }
#q { font: 14px var(--font-body); color: var(--ink); background: var(--panel); border: 1px solid var(--rule); border-radius: 4px; padding: 5px 10px; min-width: 0; flex: 1 1 180px; max-width: 280px; margin-left: auto; }
.group { display: grid; gap: 14px; }
.ghead { display: grid; gap: 2px; }
.ghead h2 { font-family: var(--font-display); font-weight: 600; font-size: 22px; margin: 0; text-wrap: balance; }
.ghead p { margin: 0; color: var(--ink-2); font-size: 14px; }
.count { font-family: var(--font-data); font-size: 12px; color: var(--muted); margin-left: 6px; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 14px; align-items: start; }
.card { background: var(--panel); border: 1px solid var(--rule); border-radius: 6px; padding: 14px 16px 12px; display: grid; gap: 6px; min-width: 0; scroll-margin-top: 70px; }
.card:target { outline: 2px solid var(--accent); outline-offset: 2px; }
.top { display: flex; justify-content: space-between; align-items: center; font-family: var(--font-data); font-size: 12px; color: var(--muted); }
.rid { color: var(--muted); text-decoration: none; font-family: var(--font-data); }
.rid:hover { color: var(--ink); text-decoration: underline; }
.st { font: 600 11px var(--font-display); letter-spacing: .06em; color: var(--good); border: 1px solid currentColor; border-radius: 3px; padding: 0 5px; }
.head { font-family: var(--font-data); font-weight: 500; font-size: 26px; line-height: 1.15; margin: 4px 0 0; font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
.card h3 { font-family: var(--font-display); font-weight: 600; font-size: 17px; line-height: 1.2; margin: 0; text-wrap: balance; }
.cap { margin: 0; font-size: 13.5px; color: var(--ink-2); }
.verdict { margin: 2px 0 0; font-size: 13px; font-weight: 500; padding: 4px 8px; border-radius: 4px; background: var(--accent-soft); }
.verdict .vk { font: 600 11px var(--font-display); letter-spacing: .06em; text-transform: uppercase; margin-right: 4px; color: var(--ink-2); }
.verdict[data-v="pass"] { box-shadow: inset 3px 0 0 var(--good); }
.verdict[data-v="fail"] { box-shadow: inset 3px 0 0 var(--crit); }
.verdict[data-v="mixed"] { box-shadow: inset 3px 0 0 var(--warn); }
.verdict[data-v="none"] { box-shadow: inset 3px 0 0 var(--na); }
.chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 2px; }
.chip { font: 500 11px var(--font-data); color: var(--ink-2); border: 1px solid var(--rule); border-radius: 3px; padding: 0 5px; max-width: 100%; overflow-wrap: anywhere; }
.chip.gas { color: var(--bar); border-color: currentColor; }
.chip.crux { color: var(--accent); border-color: currentColor; }
.chip.tag em { font-style: normal; }
details { border-top: 1px solid var(--rule); margin-top: 4px; padding-top: 6px; }
summary { font: 600 12px var(--font-display); letter-spacing: .04em; color: var(--muted); cursor: pointer; text-transform: uppercase; }
summary:hover { color: var(--ink); }
.claim { font-size: 13px; margin: 8px 0; }
dl { display: grid; grid-template-columns: 72px minmax(0, 1fr); gap: 4px 8px; margin: 0; font-size: 12.5px; }
dt { color: var(--muted); font-family: var(--font-display); font-weight: 600; }
dd { margin: 0; color: var(--ink-2); overflow-wrap: anywhere; }
code { font-family: var(--font-data); font-size: .92em; overflow-wrap: anywhere; }
.others { background: var(--panel); border: 1px solid var(--rule); border-radius: 6px; padding: 16px; display: grid; gap: 10px; }
.others h2 { font-family: var(--font-display); font-weight: 600; font-size: 20px; margin: 0; }
.others p { margin: 0; color: var(--ink-2); font-size: 14px; max-width: 75ch; }
.others ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px; }
.others li { display: grid; grid-template-columns: 40px 24px minmax(0, 1fr); gap: 8px; align-items: baseline; font-size: 13px; }
.st-E { color: var(--warn); } .st-S { color: var(--na); } .st-U { color: var(--crit); } .st-B { color: var(--na); }
.others .chip { text-align: center; border-color: currentColor; }
.empty { color: var(--muted); }
footer { color: var(--muted); font-size: 12px; display: grid; gap: 4px; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
@media (max-width: 760px) { .bar { position: static; } }
@media (max-width: 520px) { .head { font-size: 22px; } #q { max-width: none; margin-left: 0; } }
</style>
<div class="wrap">
<header>
  <span class="eyebrow">CVIN · claim register · results of record</span>
  <h1>Result cards</h1>
  <p class="lede">Every verified result in the claim register, one card each. A card gives the value as the register states it, the conditions it was measured under, and its pre-registered verdict where there is one. Open a card for the register row behind it. The results board shows the same evidence as panels and charts.</p>
  <div class="kpis">
    <div class="kpi"><span class="k">__VCOUNT__</span><span class="l">verified results (V)</span></div>
    <div class="kpi"><span class="k">__PREREG__</span><span class="l">with a pre-registered verdict</span></div>
    <div class="kpi"><span class="k">__GAS__</span><span class="l">gas results with a class</span></div>
    <div class="kpi"><span class="k">__ROWS__</span><span class="l">register rows (__STATUS__)</span></div>
  </div>
</header>
<nav class="bar" aria-label="Filter cards">__FILTERS__<input id="q" type="search" placeholder="Search cards" aria-label="Search cards"></nav>
<main class="wrap-inner" style="display:grid;gap:32px">__SECTIONS__
<p class="empty" id="none" hidden>No card matches. Clear the search or pick All.</p>
<section class="others"><h2>Not results of record (__NOTV__)</h2>
<p>These register rows are estimates (E), superseded (S) or unsupported by the trunk (U). They have no card and no headline value, and none of them may be quoted as a result.</p>
<ul>__OTHERS__</ul></section>
</main>
<footer>
  <span>Generated by <code>docs/figures/make_result_cards.py</code> from <code>docs/MEASUREMENT_CONDITIONS.md</code>, <code>docs/figures/dashboard_snapshot.json</code> and <code>docs/testing/gas_charter.py</code>. CI fails if a verified row has no card, or if a card's value is not in its row.</span>
  <span>Chips: measurement conditions tag (grey), gas class (blue), thesis crux (amber). Author: Nikhil Prakash (MASc, UBC ECE).</span>
</footer>
</div>
<script>
(function () {
  var mode = "all", q = "";
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var groups = Array.prototype.slice.call(document.querySelectorAll(".group"));
  var buttons = Array.prototype.slice.call(document.querySelectorAll(".f"));
  function apply() {
    var shown = 0;
    cards.forEach(function (c) {
      var ok = (mode === "all" || (mode === "pre" ? c.dataset.pre === "1" : c.dataset.group === mode)) &&
               (!q || c.dataset.text.indexOf(q) !== -1);
      c.hidden = !ok; if (ok) shown++;
    });
    groups.forEach(function (g) { g.hidden = !g.querySelector(".card:not([hidden])"); });
    document.getElementById("none").hidden = shown > 0;
  }
  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      mode = b.dataset.f;
      buttons.forEach(function (x) { var on = x === b; x.classList.toggle("on", on); x.setAttribute("aria-pressed", on ? "true" : "false"); });
      apply();
    });
  });
  document.getElementById("q").addEventListener("input", function (e) { q = e.target.value.trim().toLowerCase(); apply(); });
})();
</script>
"""


def main():
    page, problems = build()
    for p in problems:
        print("PROBLEM:", p)
    if "--check" in sys.argv:
        stale = not OUT.exists() or OUT.read_text() != page
        if stale:
            print("STALE: run python3 docs/figures/make_result_cards.py")
        if not (stale or problems):
            print(f"result cards current; {len(CARDS)} cards, every V row carded, every value in its row")
        return 1 if (stale or problems) else 0
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page)} bytes)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
