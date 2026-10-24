#!/usr/bin/env python3
"""Build a self-contained replay page: replay.html with a trace embedded.

The output opens from file:// with no file picker and no server, so it can be
emailed, put on a USB stick, or opened in a defence room offline.

    python3 build_replay.py TRACE.jsonl OUT.html [--thin N] [--max-mb 25]

--thin N keeps every Nth `step` event (positions) and drops the others; `tx`,
`safety`, `attack`, `enroll`, `meta` and `summary` events are never thinned,
so every counter in the replay stays exact. Input is cvin-v2v-trace/1, plain or .gz. Without --thin, the builder thins
automatically (2, 3, 4, ...) until the page fits under --max-mb.
"""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parents[2] / "docs" / "visual" / "replay" / "replay.html"
MARKER = '<script id="embedded-trace" type="application/x-ndjson"></script>'


def thinned(lines, n):
    out = []
    for line in lines:
        if n > 1 and '"type":"step"' in line[:16]:
            k = thinned.counter = getattr(thinned, "counter", -1) + 1
            if k % n:
                continue
        out.append(line)
    return out


def build(trace, out, thin=None, max_mb=25.0):
    template = TEMPLATE.read_text()
    if MARKER not in template:
        sys.exit(f"{TEMPLATE}: embedded-trace marker not found")
    import gzip
    opener = gzip.open if str(trace).endswith(".gz") else open
    with opener(trace, "rt") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    n = thin or 1
    while True:
        thinned.counter = -1
        body = "\n".join(thinned(lines, n)).replace("</script", "<\\/script")
        page = template.replace(
            MARKER, '<script id="embedded-trace" type="application/x-ndjson">\n'
            + body + "\n</script>")
        size_mb = len(page.encode()) / 1e6
        if thin or size_mb <= max_mb or n >= 50:
            break
        n += 1
    if n > 1:
        # Playback timing reads snapshot_every from the header; keep it truthful.
        page = page.replace('"schema":"cvin-v2v-trace/1"', f'"schema":"cvin-v2v-trace/1","snapshot_every":{n}', 1)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_text(page)
    print(f"wrote {out}: {size_mb:.1f} MB, snapshots thinned 1/{n}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trace")
    ap.add_argument("out")
    ap.add_argument("--thin", type=int, default=None)
    ap.add_argument("--max-mb", type=float, default=25.0)
    a = ap.parse_args()
    build(a.trace, a.out, a.thin, a.max_mb)


if __name__ == "__main__":
    main()
