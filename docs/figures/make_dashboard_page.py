#!/usr/bin/env python3
"""Render the results dashboard page from the generated snapshot (plan 2026-10-09 P1.3).

    python3 docs/figures/make_dashboard_data.py   # first: the snapshot from committed results
    python3 docs/figures/make_dashboard_page.py   # then: docs/figures/results_dashboard.html

The page embeds the snapshot verbatim; it contains no number of its own.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
snap = json.loads((HERE / "dashboard_snapshot.json").read_text())
# drop the per-row register dump from the page (it is in the snapshot file); keep the page light
snap.pop("register_rows", None)
payload = json.dumps(snap, ensure_ascii=False).replace("</", "<\\/")
html = (HERE / "dashboard_template.html").read_text().replace("__SNAPSHOT__", payload)
(HERE / "results_dashboard.html").write_text(html)
print("wrote docs/figures/results_dashboard.html", len(html), "bytes")
