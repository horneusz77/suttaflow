"""Typed, revision-bound issue evidence; never a publication or human-review grant."""
from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
import re

ISSUE_STATUSES = frozenset({"PROPOSED", "OPEN", "IN_PROGRESS", "RESOLVED"})
ISSUE_SEVERITIES = {
    "CRITICAL": "CRITICAL", "MAJOR": "MAJOR", "MINOR": "MINOR", "NOTE": "NOTE",
    "P0": "CRITICAL", "P1": "MAJOR", "P2": "MINOR",
}


def _id(value) -> bool:
    return isinstance(value, str) and bool(value) and not any(c.isspace() or c == "\0" for c in value)


def _sha(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate(root: Path, capdir: Path, groups: list[dict], decisions: dict) -> list[dict]:
    """Require a real current report for OPEN or critical/major issues.

    Historical decisions are read unchanged. A proposed decision or an issue ID
    records a question, not its closure. The report binding checks bytes, scope,
    date and the recorded reviewer; it does not authenticate that person's identity.
    """
    problems = []

    def fail(code, item, msg=""):
        problems.append({"code": code, "item": str(item), "msg": msg})

    if not isinstance(decisions, dict):
        fail("DECISION_RECORD_INVALID", "decisions")
        return problems
    records, statuses, severities = {}, {}, {}
    for collection in ("decisions", "minor_revisions_proposed"):
        entries = decisions.get(collection, [])
        if not isinstance(entries, list):
            fail("DECISION_RECORD_INVALID", collection)
            continue
        for index, record in enumerate(entries):
            if not isinstance(record, dict) or not _id(record.get("id")):
                fail("DECISION_ID_INVALID", f"{collection}[{index}]")
                continue
            if record["id"] in records:
                fail("DECISION_DUPLICATE_ID", record["id"])
                continue
            issue = record["id"]
            records[issue] = record
            # Legacy minor proposals have no status field; the collection name
            # supplies PROPOSED, never RESOLVED. Preserve every original byte.
            status = record.get("status", "PROPOSED" if collection == "minor_revisions_proposed" else None)
            if not isinstance(status, str) or status not in ISSUE_STATUSES:
                fail("DECISION_STATUS_INVALID", issue)
            statuses[issue] = status
            # Historical proposals carry no priority. Only an absent field is
            # unprioritized; null, empty and unknown explicit values are errors.
            severity = record.get("severity")
            if "severity" in record and (not isinstance(severity, str) or severity not in ISSUE_SEVERITIES):
                fail("DECISION_SEVERITY_INVALID", issue)
            severities[issue] = ISSUE_SEVERITIES.get(severity) if isinstance(severity, str) else None
    targets: dict[str | None, dict[str, set[str]]] = {}
    for group in groups:
        issue = group.get("issue")
        needs_record = group["status"] in ("OPEN", "VARIANT", "MINOR")
        if needs_record and (not _id(issue) or issue not in records):
            fail("DECISION_MISSING", issue or ",".join(group["pali"]))
            continue
        if group["status"] == "OPEN" or (_id(issue) and (
                statuses.get(issue) in ("OPEN", "IN_PROGRESS") or severities.get(issue) in ("CRITICAL", "MAJOR"))):
            target = targets.setdefault(issue, {"pali": set(), "pl": set()})
            for side in target:
                target[side].update(group[side])
    for issue in records:
        if statuses[issue] in ("OPEN", "IN_PROGRESS") or severities[issue] in ("CRITICAL", "MAJOR"):
            targets.setdefault(issue, {"pali": set(), "pl": set()})
    entries = decisions.get("issue_resolutions", [])
    resolutions = {}
    if not isinstance(entries, list):
        fail("DECISION_RESOLUTION_INVALID", "issue_resolutions")
        entries = []
    for index, resolution in enumerate(entries):
        if not isinstance(resolution, dict) or not _id(resolution.get("issue_id")):
            fail("DECISION_RESOLUTION_INVALID", f"issue_resolutions[{index}]")
            continue
        issue = resolution["issue_id"]
        if issue in resolutions:
            fail("DECISION_RESOLUTION_DUPLICATE", issue)
        resolutions[issue] = resolution
    if not targets:
        return problems
    subject_hash = hashlib.sha256((capdir / "pl_mn41_doc.docx").read_bytes()).hexdigest()
    pali_hash = hashlib.sha256((capdir / "pali_bjt_bd.htm").read_bytes()).hexdigest()
    known = {side: {unit for group in groups for unit in group[side]} for side in ("pali", "pl")}
    for issue, required_scope in targets.items():
        resolution = resolutions.get(issue)
        record = records.get(issue, {})
        if not resolution or record.get("status") != "RESOLVED" or resolution.get("status") != "RESOLVED":
            fail("DECISION_UNRESOLVED", issue)
            continue
        if resolution.get("schema") != "suttaflow-issue-resolution-v1" \
                or not _id(resolution.get("reviewer_id")) \
                or not isinstance(resolution.get("resolution"), str) or not resolution["resolution"].strip():
            fail("DECISION_RESOLUTION_INVALID", issue)
        try:
            timestamp = dt.datetime.fromisoformat(resolution["resolved_at_utc"])
            if timestamp.tzinfo is None or timestamp > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
                raise ValueError("invalid resolution timestamp")
        except (KeyError, TypeError, ValueError):
            fail("DECISION_RESOLUTION_INVALID", issue, "resolution timestamp missing or invalid")
        if resolution.get("subject_sha256") != subject_hash or resolution.get("pali_sha256") != pali_hash:
            fail("DECISION_RESOLUTION_STALE", issue)
        scope = resolution.get("scope")
        if not isinstance(scope, dict):
            fail("DECISION_RESOLUTION_SCOPE_INVALID", issue)
        else:
            for side in ("pali", "pl"):
                units = scope.get(side)
                if not isinstance(units, list) or not units or any(not _id(unit) for unit in units):
                    fail("DECISION_RESOLUTION_SCOPE_INVALID", issue, side)
                elif len(set(units)) != len(units) or not required_scope[side] <= set(units) or not set(units) <= known[side]:
                    fail("DECISION_RESOLUTION_SCOPE_INVALID", issue, side)
        evidence = resolution.get("evidence")
        if not isinstance(evidence, dict) or not isinstance(evidence.get("path"), str) \
                or not evidence["path"].strip() or "\0" in evidence["path"] or not _sha(evidence.get("sha256")):
            fail("DECISION_RESOLUTION_EVIDENCE_INVALID", issue)
            continue
        path = root / evidence["path"]
        if Path(evidence["path"]).is_absolute() or root.resolve() not in path.resolve().parents or not path.is_file():
            fail("DECISION_RESOLUTION_EVIDENCE_INVALID", issue)
            continue
        contents = path.read_bytes()
        if not contents.strip() or hashlib.sha256(contents).hexdigest() != evidence["sha256"]:
            fail("DECISION_RESOLUTION_EVIDENCE_INVALID", issue)
    return problems
