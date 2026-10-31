#!/usr/bin/env python3
"""Generate the CVIN-SSI blueprint drawing set (docs/blueprints/sheets/*.svg).

    python3 docs/blueprints/make_blueprints.py                # all sheets
    python3 docs/blueprints/make_blueprints.py BP-1           # sheets whose number starts with BP-1
    python3 docs/blueprints/make_blueprints.py --check        # CI: fail on data drift or stale SVGs
    python3 docs/blueprints/make_blueprints.py --update-lock  # accept a deliberate re-measurement
    node docs/blueprints/render_png.js                        # PNG via Chromium

Every measured value comes from data.py, which reads the results of record.
Exit codes: 0 ok · 1 data drift, a missing/changed source, or committed SVGs
that differ from a fresh generation.
"""
import argparse
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import data  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "sheets"


def builders():
    import sheets_000 as s000
    import sheets_100 as s100
    import sheets_200 as s200
    import sheets_300 as s300
    import sheets_400 as s400
    import sheets_500 as s500
    out = []
    for mod in (s000, s100, s200, s300, s400, s500):
        out.extend(mod.SHEETS)
    return out


def generate(dest: pathlib.Path, prefix: str = "", quiet: bool = False):
    dest.mkdir(parents=True, exist_ok=True)
    bs = builders()
    for i, build in enumerate(bs, 1):
        sh = build()
        sh.sheet_no, sh.sheet_of = i, len(bs)
        if not sh.number.startswith(prefix):
            continue
        p = dest / f"{sh.number}.svg"
        p.write_text(sh.render(), encoding="utf-8")
        if not quiet:
            print("wrote", p.relative_to(HERE.parent.parent) if dest == OUT else p.name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix", nargs="?", default="")
    ap.add_argument("--check", action="store_true", help="fail on data drift or committed SVGs out of date")
    ap.add_argument("--update-lock", action="store_true", help="rewrite data.lock.json from the current results")
    a = ap.parse_args()

    try:
        drift = data.check_lock(update=a.update_lock)
    except data.DataError as e:
        print(f"DATA ERROR: {e}")
        return 1
    if drift:
        return 1

    if not a.check:
        try:
            generate(OUT, a.prefix)
        except data.DataError as e:
            print(f"DATA ERROR: {e}")
            return 1
        return 0

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        try:
            generate(tmp, quiet=True)
        except data.DataError as e:
            print(f"DATA ERROR: {e}")
            return 1
        fresh = {p.name: p.read_bytes() for p in tmp.glob("*.svg")}
    committed = {p.name: p.read_bytes() for p in OUT.glob("*.svg")}
    stale = sorted(n for n in fresh if committed.get(n) != fresh[n])
    orphan = sorted(set(committed) - set(fresh))
    print(f"{len(data.CAT)} data values match data.lock.json; {len(fresh)} sheets generated, "
          f"{len(stale)} differ from the committed SVGs, {len(orphan)} committed SVGs have no builder")
    for n in stale:
        print(f"  stale: sheets/{n}")
    for n in orphan:
        print(f"  orphan: sheets/{n}")
    if stale or orphan:
        print("Regenerate with: python3 docs/blueprints/make_blueprints.py (and render_png.js), then commit.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
