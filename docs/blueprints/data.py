"""Data layer for the blueprint set (Plan 2, phase P2).

Every measured value drawn on a sheet comes through this module. A sheet never
types a number. Two kinds of source exist:

  file      read from a result-of-record file (JSON / CSV / harness table)
  register  parsed out of a row of docs/MEASUREMENT_CONDITIONS.md (or another
            named document) by a pattern, used only where no result file holds
            the value (e.g. the W3C checker score, the attestEvent build gas)

    from data import D, raw, src
    D("gas.ERC-1056.createIdentity")      -> "52,594"   (formatted)
    raw("gas.ERC-1056.createIdentity")    -> 52594      (number)
    src("gas.ERC-1056.createIdentity")    -> ("4_comparison-framework/...json", "#25")

All values are computed once on import and compared with data.lock.json. If a
file is missing, a pattern no longer matches, or a value differs from the lock,
make_blueprints.py prints a diff and exits non-zero. After a deliberate
re-measurement, accept the new values with:

    python3 docs/blueprints/make_blueprints.py --update-lock

Not data-bound, by design (listed so the exemption is explicit):
  * EVM protocol constants on BP-102 (SSTORE 20,000, LOG 375, ...): they are the
    EVM's gas schedule, not measurements of this repository.
  * Structural counts (12 basic-set functions, 11 event types, 10 schemas,
    9 roles, 23 sheets): they describe code shape and change only with code.
  * Basic-set coverage fractions on BP-104 (11/11, 10/11, ...): copied from
    BASIC_ID_SET_EXTENSION.md section 2.2; structural, not measured.
  * Per-suite test counts on BP-202/BP-601 (28, 32 + 6, 12/12) and contract
    counts (16 contracts): descriptive inventory, not results of record.
  * Illustrative values: the block numbers in BP-103's linked-list detail and
    the non-total segments of BP-102's transaction anatomy (marked E).
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
import re
from typing import Any, Callable, Dict, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOCK = pathlib.Path(__file__).resolve().parent / "data.lock.json"
REGISTER = "docs/MEASUREMENT_CONDITIONS.md"

GAS = "4_comparison-framework/results/gas_benchmark.json"
ATTACK = "4_comparison-framework/security-analysis/results/attack_results.csv"
MATRIX = "4_comparison-framework/security-analysis/results/security_matrix.csv"
V2V = "cv2x-testbed/sumo/results/v2v_latency_stats.json"
FRESH = "cv2x-testbed/results/freshness_k.json"
PROBE = "cv2x-testbed/results/freshness_k_probe.json"
PKI = "cv2x-testbed/results/pki_vs_erc1056.json"
PARITY = "cv2x-testbed/results/lifecycle_parity.json"
LIFE = "1_blockchain-identity/results/metrics/latest/lifecycle.json"
CRUD = "1_blockchain-identity/results/metrics/latest/crud.json"
HTTP_SCALE = "1_blockchain-identity/results/metrics-rpc/latest/scale.json"
HTTP_RESOLVE = "1_blockchain-identity/results/metrics-rpc/latest/resolve.json"
RES_M0 = "docs/figures/resolution_latency_M0.json"

_cache: Dict[str, Any] = {}


class DataError(RuntimeError):
    pass


def _file(rel: str):
    if rel not in _cache:
        p = ROOT / rel
        if not p.exists():
            raise DataError(f"missing result file: {rel}")
        if rel.endswith(".json"):
            _cache[rel] = json.loads(p.read_text())
        elif rel.endswith(".csv"):
            _cache[rel] = list(csv.reader(p.open()))
        else:
            _cache[rel] = p.read_text()
    return _cache[rel]


def _row(n: int) -> str:
    text = _file(REGISTER)
    m = re.search(rf"^\| {n} \|.*$", text, re.M)
    if not m:
        raise DataError(f"register row #{n} not found")
    return m.group(0)


def _pat(text: str, pattern: str, what: str) -> str:
    m = re.search(pattern, text)
    if not m:
        raise DataError(f"pattern for {what!r} no longer matches: /{pattern}/")
    return m.group(1)


def _num(s: str) -> float:
    v = float(s.replace(",", ""))
    return int(v) if v.is_integer() and "." not in s else v


# ------------------------------------------------------------------ formats
def g(v):  # gas / integer with thousands separator
    return f"{int(v):,}"


def ms3(v):
    return f"{v:.3f}"


def ms2(v):
    return f"{v:.2f}"


def ms1(v):
    return f"{v:.1f}"


def ms4(v):
    return f"{v:.4f}"


def i0(v):
    return f"{round(v)}"


def pct1(v):
    return f"{v:.1f}%"


def asis(v):
    return str(v)


# ------------------------------------------------------------------ catalogue
# key -> (loader, formatter, source, register row)
CAT: Dict[str, Tuple[Callable[[], Any], Callable[[Any], str], str, str]] = {}


def reg(key, loader, fmt, source, row):
    CAT[key] = (loader, fmt, source, row)


# gas, register #25: every cell of the nine-standard table
def _gas_cells():
    d = _file(GAS)
    for std, ops in d.items():
        if std == "metadata":
            continue
        for op, v in ops.items():
            if isinstance(v, dict) and isinstance(v.get("gasUsed"), int):
                reg(f"gas.{std}.{op}", (lambda s=std, o=op: _file(GAS)[s][o]["gasUsed"]), g, GAS, "#25")


_gas_cells()
reg("gas.4337.indirection", lambda: _file(GAS)["ERC-4337"]["updateAttributeVia4337"]["gasUsed"]
    - _file(GAS)["ERC-4337"]["updateAttribute"]["gasUsed"], g, GAS, "#25")


def _create_sorted():
    d = _file(GAS)
    return sorted(((s, v["createIdentity"]["gasUsed"]) for s, v in d.items() if s != "metadata"), key=lambda x: x[1])


reg("gas.create.spread", lambda: _create_sorted()[-1][1] / _create_sorted()[0][1], lambda v: f"{v:.1f}×", GAS, "#25")
reg("gas.ratio.721_over_1056", lambda: raw("gas.ERC-721.createIdentity") / raw("gas.ERC-1056.createIdentity"),
    lambda v: f"≈{round(v)}×", GAS, "#25")
reg("gas.vinbound.createVehicleDID", lambda: _num(_pat(_row(6), r"createVehicleDID[^0-9]{0,40}([0-9,]{5,})", "createVehicleDID")), g, REGISTER, "#6")
reg("gas.ratio.vinbound", lambda: raw("gas.ERC-721.createIdentity") / raw("gas.vinbound.createVehicleDID"),
    lambda v: f"≈{round(v)}×", REGISTER, "#6")

# lifecycle (harness), #30/#35
def _life(adapter):
    for a in _file(LIFE):
        if a["adapter"] == adapter:
            return a
    raise DataError(f"lifecycle adapter {adapter} missing")


for ad in ("erc1056", "erc1056w", "erc721", "erc725", "erc735", "erc1155", "erc725xy", "lsp8", "erc4337", "cvin"):
    reg(f"life.{ad}.gas", (lambda a=ad: _life(a)["lifetimeGas"]), g, LIFE, "#35")
    reg(f"life.{ad}.newslots", (lambda a=ad: _life(a)["lifetimeZeroToNonzeroSstores"]), asis, LIFE, "#35")
reg("life.ratio.721", lambda: raw("life.erc721.gas") / raw("life.erc1056.gas"), lambda v: f"{v:.2f}×", LIFE, "#30")
reg("life.ratio.725", lambda: raw("life.erc725.gas") / raw("life.erc1056.gas"), lambda v: f"{v:.2f}×", LIFE, "#30")

# V2V, #27
_v = lambda pop, m, k: _file(V2V)["per_population"][pop][m][k]
reg("v2v.ssi.warm", lambda: _v("ssi", "warm", "median"), ms3, V2V, "#27")
reg("v2v.ssi.warm.lo", lambda: _v("ssi", "warm", "ci95")[0], ms3, V2V, "#27")
reg("v2v.ssi.warm.hi", lambda: _v("ssi", "warm", "ci95")[1], ms3, V2V, "#27")
reg("v2v.ssi.cold", lambda: _v("ssi", "cold", "median"), ms3, V2V, "#27")
reg("v2v.pki.warm", lambda: _v("pki", "warm", "median"), ms3, V2V, "#27")
reg("v2v.verified", lambda: _file(V2V)["totals"]["messages_verified"], g, V2V, "#27")
reg("v2v.failures", lambda: _file(V2V)["totals"]["verification_failures"], g, V2V, "#27")
reg("v2v.runs", lambda: _file(V2V)["n_runs"], asis, V2V, "#27")
reg("v2v.attacks_per_run", lambda: _file(V2V)["totals"]["verification_failures"] // _file(V2V)["n_runs"], asis, V2V, "#27")

# freshness-k, #32
def _fk(k):
    for r in _file(FRESH)["latency"]:
        if r["k"] == k:
            return r
    raise DataError(f"freshness k={k} missing")


for k in ("1", "5", "25", "inf"):
    reg(f"fk.{k}.mean", (lambda k=k: _fk(k)["mean_ms"]), ms2 if k != "inf" else ms3, FRESH, "#32")
    reg(f"fk.{k}.median", (lambda k=k: _fk(k)["median_ms"]), ms3, FRESH, "#32")
    reg(f"fk.{k}.p95", (lambda k=k: _fk(k)["p95_ms"]), ms3, FRESH, "#32")
    for f in (0.25, 0.5, 1.0):
        reg(f"fk.{k}.P{f}", (lambda k=k, f=f: math.floor(f * 100 / _fk(k)["mean_ms"])), asis, FRESH, "#32")
reg("fk.t_local", lambda: _file(FRESH)["derived"]["t_local_ms"], ms3, FRESH, "#32")
reg("fk.t_chain", lambda: _file(FRESH)["derived"]["t_chain_ms"], ms2, FRESH, "#32")
reg("fk.knee", lambda: _file(FRESH)["derived"]["k_for_Pstar_0.5_ge_100_this_run"], i0, FRESH, "#32")
reg("fk.knee.stale_s", lambda: (round(raw("fk.knee")) - 1) / 10, lambda v: f"{v:.1f} s", FRESH, "#32")
reg("probe.t_chain", lambda: _file(PROBE)["derived"]["t_chain_ms"], ms2, PROBE, "#37")


# PKI vs ERC-1056, #21
def _pki(provider, op):
    for r in _file(PKI)["results"]:
        if r["provider"] == provider and r["operation"] == op:
            return r
    raise DataError(f"pki result {provider}/{op} missing")


reg("pki.verify.median", lambda: _pki("pki_standard", "verify_message")["median_ms"], ms3, PKI, "#21")
reg("pki.verify.p95", lambda: _pki("pki_standard", "verify_message")["p95_ms"], ms3, PKI, "#21")
for f in (0.25, 0.5, 1.0):
    reg(f"pki.P{f}", (lambda f=f: math.floor(f * 100 / raw("pki.verify.median"))), asis, PKI, "#21")
for f in (0.25, 0.5, 1.0):
    reg(f"v2v.ssi.P{f}", (lambda f=f: math.floor(f * 100 / raw("v2v.ssi.warm"))), asis, V2V, "#27")


# lifecycle parity (M4), #33
def _parity(backend, op):
    for r in _file(PARITY)["results"]:
        if r["backend"] == backend and r["operation"] == op:
            return r
    raise DataError(f"parity {backend}/{op} missing")


reg("parity.mobi.birth.median", lambda: _parity("mobi_vid_v2", "birth")["median_ms"], ms2, PARITY, "#33")
reg("parity.mobi.birth.gas", lambda: _parity("mobi_vid_v2", "birth")["gas_median"], g, PARITY, "#33")


# read path, #39 (HTTP) and M0 resolve
def _http_r3(adapter, axis, value):
    for r in _file(HTTP_SCALE):
        if r["adapter"] == adapter and r["op"].startswith("R3") and r["axis"] == axis and r["value"] == value:
            return r
    raise DataError(f"http R3 {adapter} {axis}={value} missing")


reg("http.r3.erc1056.h50", lambda: _http_r3("erc1056", "h", 50)["latency"]["median"], i0, HTTP_SCALE, "#39")
reg("m0.resolve.ethr.cold", lambda: _file(RES_M0)["results"]["did:ethr"]["cold"]["median_ms"], ms4, RES_M0, "—")


# security, #28 (Lens 1 CSV) and Lens 2 matrix
def _attack_rows():
    rows = _file(ATTACK)
    head = rows[0]
    out = {}
    for r in rows[1:]:
        if r and r[0] and not r[0].startswith(("TOTAL", "Legend", "Conditions")):
            out[r[0]] = r[1:7]
        if r and r[0].startswith("TOTAL"):
            out["TOTAL"] = r[1:8]
    return head[1:7], out


reg("sec.total", lambda: _attack_rows()[1]["TOTAL"][6], asis, ATTACK, "#28")
for j in range(6):
    reg(f"sec.col{j}.total", (lambda j=j: _attack_rows()[1]["TOTAL"][j]), asis, ATTACK, "#28")
reg("sec.cells", lambda: sum(len(v) for k, v in _attack_rows()[1].items() if k != "TOTAL"), asis, ATTACK, "#28")
reg("sec.na", lambda: sum(c == "—" for k, v in _attack_rows()[1].items() if k != "TOTAL" for c in v), asis, ATTACK, "#28")


def lens1():
    """{standard: [D/—, ...]} in the CSV's column order."""
    _, rows = _attack_rows()
    return {k: ["D" if c == "DEFENDED" else ("—" if c == "—" else c) for c in v] for k, v in rows.items() if k != "TOTAL"}


def lens2():
    rows = _file(MATRIX)
    ab = {"DEFENDED": "D", "PARTIAL": "P", "VULNERABLE": "V", "N/A": "N"}
    out = {}
    for r in rows[1:]:
        if not r or r[0] in ("", "Legend") or r[0].startswith("W3C"):
            continue
        out[r[0]] = [ab[c.rstrip("*")] + ("*" if c.endswith("*") else "") for c in r[1:7]]
    return out


def create_sorted():
    return _create_sorted()


# register-only values (no result file holds them)
reg("w3c.score", lambda: _num(_pat(_row(4), r"\*\*([0-9.]+)%\*\*", "W3C score")), pct1, REGISTER, "#4")
reg("w3c.checks", lambda: _num(_pat(_row(4), r"over ([0-9]+) executed checks", "checks")), asis, REGISTER, "#4")
reg("w3c.pass", lambda: _num(_pat(_row(4), r"([0-9]+) PASS", "pass")), asis, REGISTER, "#4")
reg("w3c.partial", lambda: _num(_pat(_row(4), r"([0-9]+) PARTIAL", "partial")), asis, REGISTER, "#4")
reg("w3c.fail", lambda: _num(_pat(_row(4), r"([0-9]+) FAIL", "fail")), asis, REGISTER, "#4")
reg("w3c.ext", lambda: _pat(_row(24), r"\*\*([0-9]+/[0-9]+) generated tests\*\*", "external suite"), asis, REGISTER, "#24")
reg("attest.before", lambda: _num(_pat(_row(28), r"found-and-fixed ([0-9,]+) →", "attest before")), g, REGISTER, "#28")
reg("attest.july", lambda: _num(_pat(_row(28), r"→ ([0-9,]+) gas \(July", "attest July")), g, REGISTER, "#28")
reg("attest.now", lambda: _num(_pat(_row(28), r"run of record ([0-9,]+)", "attest now")), g, REGISTER, "#28")
reg("attest.exec", lambda: _num(_pat(_row(28), r"\*\*([0-9,]+) execution gas", "attest exec")), g, REGISTER, "#28")
reg("pstar.extrap", lambda: _num(_pat(_file("docs/LATENCY_BUDGET.md"), r"P\* ≈ ([0-9]+)\*\*", "P* extrapolated")), asis, "docs/LATENCY_BUDGET.md", "#26")
reg("canon.p1", lambda: _num(_pat(_file("docs/BASIC_ID_SET_EXTENSION.md"), r"createPresentation` ([0-9,]+)", "canon P1")), g,
    "docs/BASIC_ID_SET_EXTENSION.md", "canon S1")
reg("tests.total", lambda: _num(_pat(_file("README.md"), r"\*\*([0-9]+) automated tests green\*\*", "tests total")), asis, "README.md", "status")
reg("tests.hardhat", lambda: _num(_pat(_file("README.md"), r"\(([0-9]+) Hardhat incl", "hardhat tests")), asis, "README.md", "status")
reg("tests.python", lambda: _num(_pat(_file("README.md"), r"\+ ([0-9]+) Python across", "python tests")), asis, "README.md", "status")
reg("w3c.floor", lambda: _num(_pat(_file("README.md"), r"CI floor ([0-9.]+)%", "CI floor")), pct1, "README.md", "status")


# extra keys used by the sheets
reg("fk.t_chain1", lambda: _file(FRESH)["derived"]["t_chain_ms"], ms1, FRESH, "#32")
reg("fk.fit_pct", lambda: _num(_pat(_row(32), r"within ±([0-9]+) %", "fit tolerance")), asis, REGISTER, "#32")
reg("t9.max_age", lambda: _file(FRESH)["environment"]["freshness"]["max_age_s"], ms1, FRESH, "#32")
reg("t9.cache", lambda: _file(FRESH)["environment"]["freshness"]["replay_cache_size"], g, FRESH, "#32")
reg("http.factor", lambda: _pat(_row(39), r"latency ≈([0-9.]+–[0-9.]+)×", "http factor"), asis, REGISTER, "#39")
reg("v2v.margin", lambda: 100 / raw("v2v.ssi.warm"), lambda v: f"≈{round(v, -1):.0f}×", V2V, "#27")


def kfmt(v):
    return f"{v / 1e6:.2f}M" if v >= 1e6 else f"{round(v / 1e3)}k"


def _span(stds):
    vals = [raw(f"gas.{x}.createIdentity") for x in stds]
    return min(vals), max(vals)


reg("span.event", lambda: _span(["CVIN-Combined", "ERC-1056"]), lambda v: f"{v[0]:,}–{v[1]:,}", GAS, "#25")
reg("span.shared", lambda: _span(["ERC-1155", "LSP8", "ERC-721"]), lambda v: f"{kfmt(v[0])}–{kfmt(v[1])}", GAS, "#25")
reg("span.contract", lambda: _span(["ERC-725", "ERC-735", "ERC-725xy"]), lambda v: f"{kfmt(v[0])}–{kfmt(v[1])}", GAS, "#25")
reg("span.4337", lambda: raw("gas.ERC-4337.createIdentity"), kfmt, GAS, "#25")

# ------------------------------------------------------------------ access
_values: Dict[str, Any] = {}


def raw(key: str):
    if key not in _values:
        if key not in CAT:
            raise DataError(f"unknown data key {key!r}")
        _values[key] = CAT[key][0]()
    return _values[key]


def D(key: str) -> str:
    return CAT[key][1](raw(key))


def src(key: str) -> Tuple[str, str]:
    return CAT[key][2], CAT[key][3]


def snapshot() -> Dict[str, Dict[str, Any]]:
    out = {}
    for k in sorted(CAT):
        v = raw(k)
        out[k] = {"value": list(v) if isinstance(v, tuple) else v, "shown": D(k), "source": CAT[k][2], "row": CAT[k][3]}
    return out


def check_lock(update: bool = False) -> int:
    """Compare every value with data.lock.json. Return the number of differences."""
    snap = snapshot()
    if update or not LOCK.exists():
        LOCK.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n")
        print(f"data.lock.json written ({len(snap)} values)")
        return 0
    old = json.loads(LOCK.read_text())
    diffs = []
    for k in sorted(set(old) | set(snap)):
        a, b = old.get(k, {}).get("shown"), snap.get(k, {}).get("shown")
        if a != b:
            diffs.append((k, a, b, (snap.get(k) or old.get(k))["source"]))
    if diffs:
        print(f"DATA DRIFT: {len(diffs)} value(s) differ from data.lock.json")
        for k, a, b, s in diffs:
            print(f"  {k}: {a} -> {b}   ({s})")
        print("If the re-measurement is deliberate: make_blueprints.py --update-lock")
    return len(diffs)
reg("probe.t_local", lambda: _file(PROBE)["derived"]["t_local_ms"], ms2, PROBE, "#37")
reg("sec.defended", lambda: int(raw("sec.total").split("/")[0]), asis, ATTACK, "#28")
