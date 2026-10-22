#!/usr/bin/env python3
"""Generate the CVIN-SSI blueprint drawing set (docs/blueprints/sheets/*.svg).

    python3 docs/blueprints/make_blueprints.py            # all sheets
    python3 docs/blueprints/make_blueprints.py BP-1       # sheets whose number starts with BP-1
    node docs/blueprints/render_png.js                    # PNG via Chromium

Every number drawn here is copied from the results of record and carries its
claim-register row (docs/MEASUREMENT_CONDITIONS.md) in small type.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bplib import *  # noqa: E402,F401,F403
import sheets_000 as s000  # noqa: E402
import sheets_100 as s100  # noqa: E402
import sheets_200 as s200  # noqa: E402
import sheets_300 as s300  # noqa: E402
import sheets_400 as s400  # noqa: E402
import sheets_500 as s500  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "sheets"

BUILDERS = []
for mod in (s000, s100, s200, s300, s400, s500):
    BUILDERS.extend(mod.SHEETS)

TOTAL = len(BUILDERS)


def main(prefix: str = "") -> None:
    OUT.mkdir(exist_ok=True)
    for i, build in enumerate(BUILDERS, 1):
        sh = build()
        sh.sheet_no, sh.sheet_of = i, TOTAL
        if not sh.number.startswith(prefix):
            continue
        p = OUT / f"{sh.number}.svg"
        p.write_text(sh.render(), encoding="utf-8")
        print("wrote", p.relative_to(HERE.parent.parent))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
