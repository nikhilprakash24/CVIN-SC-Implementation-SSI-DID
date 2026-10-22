#!/usr/bin/env python3
"""One run stamp for every producer of record, JS and Python (WM-2 step A2; defect D49, audit T-F10).

A producer's *scope* is the code its run executes: the producer file, its import closure (Python
`import` statements, nested ones included; JS relative `require` calls), and the non-code inputs it
names in producers.json (contracts, compiled artifacts, toolchain config, child-process producers).
Results directories are excluded, so a run's own output does not mark the next run dirty.

    python3 tools/run_identity/stamp.py --write    # resolve producers.json -> scopes.json
    python3 tools/run_identity/stamp.py --check    # CI: exit 1 if scopes.json is stale, a producer
                                                   # is missing, or an import is left unresolved
    python3 tools/run_identity/stamp.py --show cv2x-testbed/scripts/experiment_freshness_k.py

From a producer (Python):
    sys.path.insert(0, str(ROOT / "tools" / "run_identity")); from stamp import stamp
    header.update(stamp(__file__))      # commit, code_dirty, tree_dirty, scope, scope_files, scope_sha
The JS helper (1_blockchain-identity/scripts/lib/run_stamp.js) reads the same scopes.json.
git runs with cwd = the repository root and every pathspec is root-anchored (`:(top)`), so the flag
does not depend on where the producer was started (the fault of after-action report 11).
"""
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRODUCERS = HERE / "producers.json"
SCOPES = HERE / "scopes.json"
REQUIRE = re.compile(r"""require\(\s*["'](\.{1,2}/[^"']+)["']\s*\)""")


def rel(p):
    return pathlib.Path(p).resolve().relative_to(ROOT).as_posix()


# --------------------------------------------------------------------------- import closure
def _py_imports(path):
    """(module, level, names) for every import statement in the file, nested ones included."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name, 0, []
        elif isinstance(node, ast.ImportFrom):
            yield node.module or "", node.level, [a.name for a in node.names]


def _py_candidates(base, dotted):
    parts = [p for p in dotted.split(".") if p]
    if not parts:
        return []
    out, d = [], base
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        pkg = d / part
        if (pkg / "__init__.py").is_file():
            out.append(pkg / "__init__.py")
            d = pkg
            continue
        if (d / (part + ".py")).is_file():
            out.append(d / (part + ".py"))
            return out
        if pkg.is_dir():                   # namespace package (no __init__.py)
            d = pkg
            continue
        return []
    if not out:
        return [None]                      # resolved to a namespace package: no file of its own
    return out


def _resolve_py(path, search, unresolved):
    found = []
    for module, level, names in _py_imports(path):
        if level:
            base = path.parent
            for _ in range(level - 1):
                base = base.parent
            dirs = [base]
        else:
            dirs = [path.parent] + search
        hit = None
        for d in dirs:
            c = _py_candidates(d, module) if module else [None]
            if c:
                hit = [x for x in c if x is not None]
                # `from pkg import sub`: sub may be a module
                last = (d / module.replace(".", "/")) if module else d
                for n in names:
                    if (last / (n + ".py")).is_file():
                        hit.append(last / (n + ".py"))
                    elif (last / n / "__init__.py").is_file():
                        hit.append(last / n / "__init__.py")
                break
        if hit is None and not level:
            unresolved.add(module.split(".")[0])
        found.extend(hit or [])
    return found


def _resolve_js(path):
    found = []
    for spec in REQUIRE.findall(path.read_text(encoding="utf-8")):
        base = (path.parent / spec).resolve()
        for c in (base, base.with_name(base.name + ".js"), base.with_name(base.name + ".json"), base / "index.js"):
            if c.is_file():
                found.append(c)
                break
        else:
            raise SystemExit(f"{rel(path)}: require('{spec}') does not resolve")
    return found


def closure(producer, search):
    """Every repository file the producer imports, transitively; and unresolved top-level names."""
    start = ROOT / producer
    seen, todo, unresolved = set(), [start], set()
    while todo:
        f = todo.pop()
        f = f.resolve()
        if f in seen or not f.is_file() or ROOT not in f.parents:
            continue
        seen.add(f)
        if f.suffix == ".py":
            todo.extend(_resolve_py(f, search, unresolved))
        elif f.suffix == ".js":
            todo.extend(_resolve_js(f))
    return sorted(rel(f) for f in seen), unresolved


# --------------------------------------------------------------------------- scopes.json
def _local_module_names():
    """Top-level names a repository file could be imported as (to catch an unresolved local import)."""
    names = set()
    for line in subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True,
                               check=True).stdout.split():
        p = pathlib.PurePosixPath(line)
        names.add(p.stem)
        names.update(p.parts[:-1])
    return names


def build():
    spec = json.loads(PRODUCERS.read_text())
    search = [ROOT / d for d in spec["search"]]
    local = _local_module_names() - set(spec.get("external", []))
    scopes, code, problems = {}, {}, []
    for producer in spec["producers"]:
        if not (ROOT / producer).is_file():
            problems.append(f"{producer}: listed in producers.json but not a file")
            continue
        files, unresolved = closure(producer, search)
        for name in sorted(unresolved & local):
            problems.append(f"{producer}: imports '{name}', a name a repository file has, but it does not "
                            "resolve on the declared search path (add the directory to 'search', or the name to 'external')")
        code[producer] = files

    def inputs_of(producer, stack=()):
        out = []
        for item in spec["producers"][producer]["inputs"]:
            if item.startswith("@"):
                out.extend(spec["input_sets"][item[1:]])
            elif item in spec["producers"] and item not in stack:   # a child-process producer
                out.extend(code.get(item, []))
                out.extend(inputs_of(item, stack + (producer,)))
            else:
                if not (ROOT / item).exists():
                    problems.append(f"{producer}: input {item} does not exist")
                out.append(item)
        return out

    for producer in code:
        paths = sorted(set(code[producer]) | set(inputs_of(producer)))
        scopes[producer] = {"paths": paths, "imports": len(code[producer]),
                            "results": spec["producers"][producer]["results"]}
    doc = {"_doc": "Generated by tools/run_identity/stamp.py --write from producers.json; do not edit.",
           "exclude": spec["exclude"], "scopes": scopes}
    return json.dumps(doc, indent=1, sort_keys=True) + "\n", problems


# --------------------------------------------------------------------------- the stamp
def pathspecs(paths, exclude):
    return [f":(top){p}" for p in paths] + [f":(top,exclude,glob){g}" for g in exclude]


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def scope_of(producer):
    doc = json.loads(SCOPES.read_text())
    key = rel(producer) if pathlib.Path(producer).is_absolute() else producer
    if key not in doc["scopes"]:
        raise KeyError(f"{key} is not a producer of record (tools/run_identity/producers.json)")
    return key, doc["scopes"][key]["paths"], doc["exclude"]


def stamp(producer):
    """The run-identity block for one producer. code_dirty covers its scope only; tree_dirty any file."""
    key, paths, exclude = scope_of(producer)
    code = _git("status", "--porcelain", "--", *pathspecs(paths, exclude))
    tree = _git("status", "--porcelain")
    return {"commit": _git("rev-parse", "HEAD"),
            "code_dirty": None if code is None else code != "",
            "tree_dirty": None if tree is None else tree != "",
            "scope": key, "scope_files": len(paths),
            "scope_sha": hashlib.sha256("\n".join(paths).encode()).hexdigest()[:12]}


def main(argv):
    if argv[:1] == ["--write"]:
        text, problems = build()
        SCOPES.write_text(text)
        print(f"wrote {rel(SCOPES)}: {len(json.loads(text)['scopes'])} producers")
        for p in problems:
            print("PROBLEM:", p)
        return 1 if problems else 0
    if argv[:1] == ["--check"]:
        text, problems = build()
        stale = not SCOPES.exists() or SCOPES.read_text() != text
        for p in problems:
            print("PROBLEM:", p)
        if stale:
            print(f"{rel(SCOPES)} is stale: run python3 tools/run_identity/stamp.py --write")
        if not (stale or problems):
            n = len(json.loads(text)["scopes"])
            print(f"run-identity scopes: {n} producers, each import closure inside its scope; scopes.json current")
        return 1 if (stale or problems) else 0
    if argv[:1] == ["--show"] and len(argv) == 2:
        key, paths, exclude = scope_of(argv[1])
        print("\n".join(paths))
        print(json.dumps(stamp(key), indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
