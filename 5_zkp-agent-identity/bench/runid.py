"""Run identity for Python producers (guide rules 1.1.6 and 1.1.7): commit, producing-code clean flag, host, versions."""
from __future__ import annotations

import datetime
import os
import platform
import subprocess
import sys

PRODUCING = ["5_zkp-agent-identity/zkid", "5_zkp-agent-identity/steward", "5_zkp-agent-identity/attacks",
             "5_zkp-agent-identity/bench", "5_zkp-agent-identity/circuits", "5_zkp-agent-identity/scripts",
             "5_zkp-agent-identity/contracts", "5_zkp-agent-identity/artifacts"]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def run_identity() -> dict:
    return {
        "commit": _git("rev-parse", "--short", "HEAD") or "unknown",
        "code_clean": _git("status", "--porcelain", "--", *PRODUCING) == "",
        "tree_clean": _git("status", "--porcelain") == "",
        "host": {"platform": platform.platform(), "machine": platform.machine(), "cpus": os.cpu_count(),
                 "processor": platform.processor() or None},
        "python": sys.version.split()[0],
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "seed_env": os.environ.get("CVIN_SEED"),
    }
