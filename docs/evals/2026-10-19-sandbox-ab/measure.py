#!/usr/bin/env python3
"""Compare the two sandbox arms on observable artifacts, not on their self-reports."""
import json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ACS = ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5"]


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout + p.stderr)[-1500:]


def acceptance_checks(arm: Path):
    """Black-box AC checks against the shipped CLI, independent of the arm's own tests."""
    env = dict(os.environ, TODO_FILE=str(arm / "_ac_todo.json"))
    (arm / "_ac_todo.json").unlink(missing_ok=True)
    # find an entrypoint
    cands = [p for p in arm.rglob("*.py") if p.name in ("todo.py", "__main__.py", "cli.py") and ".specify" not in str(p) and ".venv" not in str(p)]
    if (arm / "todo").is_file():
        cands.insert(0, arm / "todo")
    entry = None
    for c in cands:
        if c.name == "todo":
            entry = f"{sys.executable} {c}"
        elif c.name == "__main__.py":
            entry = f"{sys.executable} -m {c.parent.name}"
        else:
            entry = f"{sys.executable} {c}"
        if entry:
            break
    if not entry:
        return {"entry": None}

    def sh(args):
        p = subprocess.run(f"{entry} {args}", cwd=arm, shell=True, capture_output=True, text=True, env=env, timeout=30)
        return p.returncode, p.stdout.strip(), p.stderr.strip()

    res = {"entry": entry}
    rc, out, _ = sh('add "first"'); res["AC-1"] = rc == 0 and bool(out)
    id1 = out.split()[-1] if out else "1"
    sh('add "second"')
    rc, out, _ = sh("list"); res["AC-2"] = rc == 0 and "first" in out and "second" in out and out.index("first") < out.index("second")
    rc, out, err = sh("done 9999"); res["AC-3a"] = rc != 0 and bool(err)
    rc, out, err = sh(f"done {id1}"); rc2, out2, _ = sh("list"); res["AC-3b"] = rc == 0 and "first" not in out2
    res["AC-4"] = (arm / "_ac_todo.json").is_file()
    (arm / "_ac_todo.json").unlink(missing_ok=True)
    return res


def metrics(arm: Path):
    m = {"arm": arm.name}
    rc, out = run(f"{sys.executable} -m unittest discover -s tests -t . 2>&1 || {sys.executable} -m unittest discover -s tests 2>&1", arm)
    m["tests_rc"] = rc; m["tests_tail"] = out.strip().splitlines()[-1] if out.strip() else ""
    m["acceptance"] = acceptance_checks(arm)
    specs = [str(p.relative_to(arm)) for p in arm.rglob("*.md") if "specs" in p.parts and ".specify" not in p.parts]
    m["spec_artifacts"] = sorted(specs)
    prog = arm / "progress.md"
    m["progress_sections"] = re.findall(r"^##\s+(.+)$", prog.read_text(), re.M) if prog.is_file() else None
    text = prog.read_text() if prog.is_file() else ""
    m["breadcrumbs"] = [l for l in text.splitlines() if re.match(r"^(pstack|harness|ROUTING|rea):", l.strip(), re.I)]
    allmd = "\n".join(p.read_text(errors="replace") for p in arm.rglob("*.md") if ".specify" not in p.parts and "sources" not in p.parts)
    m["ac_ids_referenced"] = {ac: allmd.count(ac) for ac in ACS}
    code = [p for p in arm.rglob("*.py") if ".specify" not in p.parts and "test" not in p.name and p.name != "measure.py"]
    if (arm / "todo").is_file():
        code.append(arm / "todo")
    m["impl_loc"] = sum(len(p.read_text().splitlines()) for p in code)
    m["impl_files"] = [str(p.relative_to(arm)) for p in code]
    tests = [p for p in arm.rglob("test*.py") if ".specify" not in p.parts]
    m["test_files"] = [str(p.relative_to(arm)) for p in tests]
    rc, out = run("git log --oneline | wc -l", arm); m["commits"] = out.strip()
    o = ROOT / f"out_{arm.name}.json"
    if o.is_file():
        try:
            d = json.loads(o.read_text())
            m["usage"] = {k: d.get(k) for k in ("duration_ms", "num_turns", "total_cost_usd", "is_error")}
        except Exception as e:
            m["usage"] = f"unparsed: {e}"
    s, e = ROOT / f"start_{arm.name}", ROOT / f"end_{arm.name}"
    if s.is_file() and e.is_file():
        m["wall_s"] = int(e.read_text()) - int(s.read_text())
    return m


if __name__ == "__main__":
    for arm in ("A", "B"):
        print(json.dumps(metrics(ROOT / arm), indent=1, default=str))
