"""L4 path setup: make cv2x-testbed importable for in-process use-case tests.

cv2x-testbed/scripts/test_use_cases.py is a script, not a package; it imports
`identity.*` from cv2x-testbed/ by inserting its own parent on sys.path. We add both
cv2x-testbed/ (for `identity`) and cv2x-testbed/scripts/ (for the script module itself)
here so the test modules can simply `import test_use_cases`.
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in (ROOT / "cv2x-testbed", ROOT / "cv2x-testbed/scripts"):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
