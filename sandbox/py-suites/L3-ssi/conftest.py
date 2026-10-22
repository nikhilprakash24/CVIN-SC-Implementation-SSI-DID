import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in (ROOT / "cv2x-testbed",):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
