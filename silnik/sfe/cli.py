"""CLI: manifest | evaluate | replay. All paths go through sfe.qa.evaluate()."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unittest
from pathlib import Path

from . import qa

ROOT = Path(__file__).resolve().parent.parent


def dump(o) -> bytes:
    return (json.dumps(o, ensure_ascii=False, sort_keys=True, indent=1) + "\n").encode("utf-8")


def stable(report: dict) -> dict:
    return report  # evaluate() output contains no timestamps; kept for clarity


def cmd_manifest(a) -> int:
    m = qa.build_manifest(ROOT)
    (ROOT / "anchors").mkdir(exist_ok=True)
    (ROOT / "anchors" / "release_manifest.json").write_bytes(dump(m))
    print(json.dumps({"files": len(m["files"]), "manifest_core_sha256": m["manifest_core_sha256"]}))
    return 0


def cmd_evaluate(a) -> int:
    r = qa.evaluate(ROOT, expected_anchor=a.expect_anchor, attestations=a.attestations)
    out = ROOT / "build" / "qa_report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(dump(r))
    h = hashlib.sha256(dump(r)).hexdigest()
    (ROOT / "anchors" / "report_lock.json").write_bytes(dump({"qa_report_sha256": h}))
    print(json.dumps({k: r[k] for k in ("verdict", "TECHNICAL_EVIDENCE_READY", "FULL_COVERAGE_REVIEW_READY",
                                         "HUMAN_PALIST_REVIEW", "ready_for_publication")} | {"errors": len(r["errors"]),
                     "report_sha256": h}, ensure_ascii=False))
    return 0 if r["TECHNICAL_EVIDENCE_READY"] else 2


def cmd_replay(a) -> int:
    """Regenerate the report from inputs and compare with the stored report AND its lock."""
    r = qa.evaluate(ROOT, expected_anchor=a.expect_anchor, attestations=a.attestations)
    fresh = dump(r)
    stored = (ROOT / "build" / "qa_report.json").read_bytes() if (ROOT / "build" / "qa_report.json").is_file() else b""
    lock = json.loads((ROOT / "anchors" / "report_lock.json").read_text()) if (ROOT / "anchors" / "report_lock.json").is_file() else {}
    problems = []
    if stored != fresh:
        problems.append("STORED_REPORT_STALE_OR_TAMPERED")
    if lock.get("qa_report_sha256") != hashlib.sha256(fresh).hexdigest():
        problems.append("REPORT_LOCK_MISMATCH")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    counted = suite.countTestCases()
    res = unittest.TextTestRunner(stream=open(Path(a.test_log), "w", encoding="utf-8") if a.test_log else sys.stderr,
                                  verbosity=1).run(suite) if a.run_tests else None
    out = {"replay": "REPLAY_CONSISTENT" if not problems else "REPLAY_HOLD", "problems": problems,
           "verdict": r["verdict"], "tests_discovered": counted,
           "tests_run": res.testsRun if res else None,
           "tests_failed": (len(res.failures) + len(res.errors)) if res else None,
           "ready_for_publication": False}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if not problems and (res is None or res.wasSuccessful()) else 3


def main() -> int:
    ap = argparse.ArgumentParser(prog="python -m sfe.cli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifest")
    for name in ("evaluate", "replay"):
        p = sub.add_parser(name)
        p.add_argument("--expect-anchor", help="manifest_core_sha256 published outside the package")
        p.add_argument("--attestations", type=Path)
        if name == "replay":
            p.add_argument("--run-tests", action="store_true")
            p.add_argument("--test-log")
    a = ap.parse_args()
    return {"manifest": cmd_manifest, "evaluate": cmd_evaluate, "replay": cmd_replay}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
