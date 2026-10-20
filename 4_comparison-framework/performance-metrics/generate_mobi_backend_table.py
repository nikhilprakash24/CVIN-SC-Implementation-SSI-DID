#!/usr/bin/env python3
"""
generate_mobi_backend_table.py

H4 evidence generator. Reads ../results/mobi_vid_backends.json (produced by
1_blockchain-identity/scripts/mobi_vid_backend_sweep.js) and emits thesis-ready
tables for "MOBI VID realizable across backends":

  ../results/mobi_vid_backends.csv  - machine-readable table
  ../results/mobi_vid_backends.tex  - LaTeX booktabs tabular

Layout: BACKENDS AS ROWS. Columns = the three MOBI VID canonical operations
(measured gasUsed) + a fidelity score (count of natively-supported concepts
out of 5: birth anchoring, lifecycle events, multi-party attestation,
verifiable claims, revocation). Gas cells for a non-native / approximate
mapping are marked with a dagger; a null gas (concept absent) is an em dash.

Usage:
  python3 generate_mobi_backend_table.py [path/to/mobi_vid_backends.json]
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE.parent / "results"
DEFAULT_INPUT = RESULTS_DIR / "mobi_vid_backends.json"

NULL_DISPLAY = "—"  # em dash
APPROX_MARK = "†"   # dagger: non-native / approximate mapping


def tex_escape(s: str) -> str:
    replacements = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in s)


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    backends = data["backends"]
    meta = data["metadata"]
    ops = meta["operations"]
    op_labels = meta.get("operationLabels", {op: op for op in ops})
    concepts = meta["fidelityConcepts"]
    return backends, ops, op_labels, concepts, meta


def cell_gas_display(cell, plain=False):
    """Return (text, is_approx). plain=True -> no markup around the dagger."""
    g = cell.get("gasUsed")
    if g is None:
        return NULL_DISPLAY, False
    approx = not cell.get("nativeSupport", True)
    num = f"{g:,}" if not plain else str(g)
    if approx:
        return f"{num}{APPROX_MARK}", True
    return num, False


def write_csv(backends, ops, op_labels, concepts, meta, out_path: Path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        header = ["backend"]
        for op in ops:
            header.append(f"{op_labels.get(op, op)} gasUsed")
            header.append(f"{op_labels.get(op, op)} native")
        header += [f"fidelity (/{len(concepts)})"] + concepts
        w.writerow(header)

        for name, b in backends.items():
            row = [name]
            for op in ops:
                c = b[op]
                g = c.get("gasUsed")
                row.append(NULL_DISPLAY if g is None else g)
                row.append("yes" if c.get("nativeSupport") else "no")
            fid = b["fidelity"]
            row.append(f"{fid['score']}/{fid['outOf']}")
            row += ["yes" if fid.get(c) else "no" for c in concepts]
            w.writerow(row)

        w.writerow([])
        w.writerow([
            "Legend",
            "gasUsed = exact receipt.gasUsed of one native-mapped tx; "
            "'native=no' cells are the closest honest approximation (concept "
            "not natively supported by the backend).",
        ])
        w.writerow([
            "Conditions",
            f"solc {meta.get('solcVersion','?')} (optimizer 200, viaIR)",
            f"OpenZeppelin {meta.get('ozVersion','?')}",
            f"network {meta.get('network','?')} chainId {meta.get('chainId','?')}",
            f"measured {meta.get('date','?')}",
        ])
    print(f"Wrote {out_path}")


def write_tex(backends, ops, op_labels, concepts, meta, out_path: Path):
    date = meta.get("date", "")
    try:
        date_h = datetime.fromisoformat(date.replace("Z", "+00:00")).astimezone(
            timezone.utc
        ).strftime("%Y-%m-%d")
    except ValueError:
        date_h = date or "n/a"

    caption = (
        "Realization of MOBI VID's three canonical operations across blockchain "
        "identity backends (rows: backends). Each operation cell reports the "
        "measured \\texttt{gasUsed} of one transaction using the backend's "
        "native primitives on the existing contract; a dagger (\\dag) marks a "
        "non-native / approximate mapping (the backend genuinely lacks the "
        "concept, so the figure is the closest honest analogue, not a faithful "
        "realization). The final column is the fidelity score: the count of the "
        "five MOBI VID concepts (birth anchoring, lifecycle events, multi-party "
        "attestation, verifiable claims, revocation) the backend supports "
        "natively. "
        f"Measured on a local Hardhat network (chain id {meta.get('chainId', 31337)}) "
        f"with Solidity {meta.get('solcVersion', '?')} (optimizer, 200 runs, "
        f"via-IR) and OpenZeppelin {meta.get('ozVersion', '?')}, {date_h}."
    )

    n_concepts = len(concepts)
    col_spec = "l" + "r" * len(ops) + "c"
    lines = [
        "% Auto-generated by generate_mobi_backend_table.py -- do not edit by hand.",
        "% Requires \\usepackage{booktabs}. \\dag is standard LaTeX.",
        "\\begin{table}[htbp]",
        "  \\centering",
        f"  \\caption{{{caption}}}",
        "  \\label{tab:mobi-vid-backends}",
        "  \\footnotesize",
        "  \\setlength{\\tabcolsep}{5pt}",
        "  \\resizebox{\\textwidth}{!}{%",
        f"  \\begin{{tabular}}{{{col_spec}}}",
        "    \\toprule",
        "    Backend & "
        + " & ".join(tex_escape(op_labels.get(op, op)) for op in ops)
        + f" & Fidelity ($/{n_concepts}$) \\\\",
        "    \\midrule",
    ]

    for name, b in backends.items():
        cells = []
        for op in ops:
            c = b[op]
            g = c.get("gasUsed")
            if g is None:
                cells.append("\\textemdash")
            elif not c.get("nativeSupport", True):
                cells.append(f"{g:,}\\,\\dag")
            else:
                cells.append(f"{g:,}")
        fid = b["fidelity"]
        cells.append(f"{fid['score']}/{fid['outOf']}")
        lines.append(f"    {tex_escape(name)} & " + " & ".join(cells) + " \\\\")

    lines += [
        "    \\bottomrule",
        "  \\end{tabular}}",
        "\\end{table}",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    if not input_path.exists():
        sys.exit(
            f"Input not found: {input_path}\n"
            "Run the sweep first:\n"
            "  cd 1_blockchain-identity && "
            "npx hardhat run scripts/mobi_vid_backend_sweep.js"
        )
    backends, ops, op_labels, concepts, meta = load(input_path)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(backends, ops, op_labels, concepts, meta, RESULTS_DIR / "mobi_vid_backends.csv")
    write_tex(backends, ops, op_labels, concepts, meta, RESULTS_DIR / "mobi_vid_backends.tex")


if __name__ == "__main__":
    main()
