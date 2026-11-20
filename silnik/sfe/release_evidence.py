"""Versioned, content-bound evidence for the release 2.0 gates.

This verifies evidence; it does not issue authority. The trusted intake process
must obtain the owner ledger and authenticated source records. Hashes prove byte
identity, not that a person read or approved those bytes. Legacy decisions and
missing attestations are never upgraded or manufactured here.

Rules: SF-RULE-STA-002/003/004, SRC-003/004, CORE-002, MAP-006.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

SHA256 = re.compile(r"^[0-9a-f]{64}$")
ISSUE_STATES = {"OPEN", "IN_PROGRESS", "RESOLVED", "REJECTED_WITH_EVIDENCE", "ACCEPTED_NONBLOCKING"}
SEVERITIES = {"P0", "P1", "P2", "P3", "INFO", "CRITICAL", "MAJOR", "MINOR", "NOTE"}
CRITICAL = {"P0", "P1", "CRITICAL", "MAJOR"}
ENVELOPE_FIELDS = {'schema', 'subject', 'core', 'r0', 'read_order', 'author_report',
                   'reviewer_report', 'human_review', 'hh_licence', 'gates', 'final_editor_acceptance'}


class EvidenceError(ValueError):
    """Expected missing, malformed, mismatched, or stale evidence."""


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def scope(value):
    if not isinstance(value, list) or not value or not all(nonempty(x) for x in value):
        raise EvidenceError("scope must be a nonempty array of unit IDs")
    if len(set(value)) != len(value):
        raise EvidenceError("duplicate scope unit IDs")
    return value


def timestamp(value, *, now=None):
    if not nonempty(value):
        raise EvidenceError("timestamp is absent")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise EvidenceError("invalid timestamp") from exc
    if dt.tzinfo is None:
        raise EvidenceError("timestamp must include timezone")
    if dt > (now or datetime.now(timezone.utc)):
        raise EvidenceError("future timestamp")
    return dt


def _unique_json_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise EvidenceError("duplicate JSON object key")
        obj[key] = value
    return obj


def _invalid_json_constant(value):
    raise EvidenceError("non-finite JSON number: " + value)


def read_artifact(root, ref, *, json_object=False):
    if root is None or not isinstance(ref, dict):
        raise EvidenceError("artifact root or reference absent")
    if not nonempty(ref.get("path")) or not isinstance(ref.get("sha256"), str) or not SHA256.fullmatch(ref["sha256"]):
        raise EvidenceError("artifact path or SHA-256 invalid")
    if type(ref.get("bytes")) is not int or ref["bytes"] <= 0:
        raise EvidenceError("artifact byte size must be positive")
    try:
        base = Path(root).resolve()
        rel = Path(ref["path"])
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        raise EvidenceError("artifact root or path cannot be resolved") from exc
    if rel.is_absolute() or ".." in rel.parts:
        raise EvidenceError("artifact path must be inside the evidence root")
    try:
        path = (base / rel).resolve()
    except (OSError, ValueError, RuntimeError) as exc:
        raise EvidenceError("artifact path cannot be resolved") from exc
    if not path.is_relative_to(base):
        raise EvidenceError("artifact symlink escapes evidence root")
    try:
        if not path.is_file():
            raise EvidenceError("artifact must be a regular file")
        raw = path.read_bytes()
    except (OSError, ValueError) as exc:
        raise EvidenceError("artifact bytes unavailable: " + ref["path"]) from exc
    if len(raw) != ref["bytes"] or hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise EvidenceError("artifact hash or byte size differs: " + ref["path"])
    if not json_object:
        return raw
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_object,
                         parse_constant=_invalid_json_constant)
    except (ValueError, UnicodeError) as exc:
        raise EvidenceError("artifact is not valid UTF-8 JSON") from exc
    if not isinstance(obj, dict):
        raise EvidenceError("artifact must contain a JSON object")
    return obj


def subject_from(evidence, root, *, subject_id=None, revision_id=None):
    if not isinstance(evidence, dict) or evidence.get("schema") != "suttaflow-release-evidence-v2":
        raise EvidenceError("release evidence schema absent or unknown")
    if set(evidence) - ENVELOPE_FIELDS:
        raise EvidenceError('unknown v2 envelope fields: ' + ', '.join(sorted(set(evidence) - ENVELOPE_FIELDS)))
    s = evidence.get("subject")
    if not isinstance(s, dict) or not nonempty(s.get("subject_id")) or not nonempty(s.get("revision_id")):
        raise EvidenceError("subject identity absent")
    if subject_id != s["subject_id"] or revision_id != s["revision_id"]:
        raise EvidenceError("subject ID or revision differs from status record")
    scope(s.get("scope"))
    read_artifact(root, s.get("content"))
    return s


def binding(record, subject, *, partial=False):
    if not isinstance(record, dict) or not isinstance(subject, dict):
        raise EvidenceError("bound record or verified subject absent")
    for k in ("subject_id", "revision_id"):
        if record.get(k) != subject.get(k):
            raise EvidenceError(k + " differs")
    if record.get("content_sha256") != subject["content"]["sha256"]:
        raise EvidenceError("content hash differs")
    units = scope(record.get("scope"))
    expected = scope(subject.get("scope"))
    mismatch = not set(units).issubset(expected) if partial else units != expected
    if mismatch:
        raise EvidenceError("scope differs from verified subject")


def consent(owner, decision_id, kind, subject, root):
    if not isinstance(owner, dict) or not nonempty(owner.get("owner_id")) or not nonempty(decision_id):
        raise EvidenceError("typed owner identity or decision ID absent")
    decisions = owner.get("typed_decisions")
    if not isinstance(decisions, list) or not all(isinstance(d, dict) for d in decisions):
        raise EvidenceError("typed owner decision ledger absent or malformed")
    ids = [d.get("id") for d in decisions]
    if not all(nonempty(x) for x in ids) or len(set(ids)) != len(ids):
        raise EvidenceError("typed decision IDs invalid or duplicated")
    matches = [d for d in decisions if d["id"] == decision_id]
    if len(matches) != 1:
        raise EvidenceError("exact typed owner decision not found")
    d = matches[0]
    if kind not in {"PUBLICATION_CONSENT", "HUMAN_REVIEW_WAIVER"} or d.get("kind") != kind or d.get("status") != "APPROVED":
        raise EvidenceError("decision purpose or status does not authorize this action")
    if d.get("owner_id") != owner["owner_id"]:
        raise EvidenceError("owner identity differs")
    binding(d, subject)
    timestamp(d.get("issued_at"))
    proof = read_artifact(root, d.get("evidence"), json_object=True)
    for key in ("id", "kind", "status", "owner_id", "subject_id", "revision_id", "content_sha256", "scope", "issued_at"):
        if proof.get(key) != d.get(key):
            raise EvidenceError("decision source does not match normalized field: " + key)
    src = proof.get("authenticated_source")
    if not nonempty(proof.get("verbatim")) or not isinstance(src, dict) or src.get("actor_id") != owner["owner_id"] or not all(nonempty(src.get(k)) for k in ("uri", "record_id")):
        raise EvidenceError("authenticated owner source record absent")
    return d


def issue_closed(issue, subject, root, *, closed_at, allow_notes=False):
    if not isinstance(issue, dict) or not nonempty(issue.get("id")) or not isinstance(issue.get("severity"), str) or issue["severity"] not in SEVERITIES or not isinstance(issue.get("status"), str) or issue["status"] not in ISSUE_STATES:
        raise EvidenceError("issue identity, severity or state invalid")
    is_note = issue["status"] == "ACCEPTED_NONBLOCKING"
    if is_note and (not allow_notes or issue["severity"] in CRITICAL):
        raise EvidenceError("critical issue or unapproved note cannot be waived")
    if issue["status"] not in {"RESOLVED", "REJECTED_WITH_EVIDENCE", "ACCEPTED_NONBLOCKING"}:
        raise EvidenceError("issue remains open: " + issue["id"])
    affected = scope(issue.get('scope'))
    if not set(affected).issubset(scope(subject.get('scope'))):
        raise EvidenceError('issue scope is outside the verified subject')
    resolution = read_artifact(root, issue.get("resolution"), json_object=True)
    binding(resolution, subject, partial=True)
    expected_kind = {'RESOLVED': 'ISSUE_RESOLUTION',
                     'REJECTED_WITH_EVIDENCE': 'ISSUE_REJECTION',
                     'ACCEPTED_NONBLOCKING': 'NONBLOCKING_NOTE_ASSESSMENT'}[issue['status']]
    if resolution.get('kind') != expected_kind or resolution.get('status') != issue['status']:
        raise EvidenceError('resolution kind or closed status differs from the issue')
    if set(resolution['scope']) != set(affected):
        raise EvidenceError('resolution scope does not match all affected issue units')
    if timestamp(resolution.get("completed_at")) > timestamp(closed_at):
        raise EvidenceError('issue resolution was completed after the report that closes it')
    if resolution.get("issue_id") != issue["id"] or not nonempty(resolution.get("reason")) or not nonempty(resolution.get("verified_by")):
        raise EvidenceError("issue resolution lacks matching verification")
    if is_note and (resolution.get("kind") != "NONBLOCKING_NOTE_ASSESSMENT" or resolution.get("meaning_change_possible") is not False):
        raise EvidenceError("individual nonblocking assessment absent")


def report(root, ref, kind, subject, *, partial=False):
    r = read_artifact(root, ref, json_object=True)
    binding(r, subject, partial=partial)
    if r.get("kind") != kind or r.get("result") not in ("PASS", "PASS_WITH_NOTES"):
        raise EvidenceError("required report kind or completed result absent: " + kind)
    completed = timestamp(r.get("completed_at"))
    if 'recorded_at' in r and timestamp(r['recorded_at']) < completed:
        raise EvidenceError('report recording precedes actual completion')
    if not isinstance(r.get("checks"), list) or not r["checks"] or not all(nonempty(x) for x in r["checks"]):
        raise EvidenceError("report checks absent")
    actor = r.get("actor")
    if not isinstance(actor, dict) or not all(nonempty(actor.get(k)) for k in ("id", "model", "context_id")):
        raise EvidenceError("report actor, model or context absent")
    findings = r.get("findings")
    if not isinstance(findings, list):
        raise EvidenceError("report findings ledger absent")
    ids = [i.get("id") if isinstance(i, dict) else None for i in findings]
    if not all(nonempty(x) for x in ids) or len(ids) != len(set(ids)):
        raise EvidenceError("report issue IDs invalid or duplicated")
    for issue in findings:
        issue_closed(issue, subject, root, closed_at=r['completed_at'],
                     allow_notes=r["result"] == "PASS_WITH_NOTES")
    if r["result"] == "PASS_WITH_NOTES" and not any(i["status"] == "ACCEPTED_NONBLOCKING" for i in findings):
        raise EvidenceError("PASS_WITH_NOTES must identify its individual notes")
    return r


def full_ai(evidence, subject, root):
    if "core" in evidence:
        subject = core_view(evidence, subject, root)
    author = report(root, evidence.get("author_report"), "AUTHOR_SELF_CHECK", subject)
    reviewer = report(root, evidence.get("reviewer_report"), "INDEPENDENT_REVIEW", subject)
    if author["actor"]["context_id"] == reviewer["actor"]["context_id"]:
        raise EvidenceError("author and reviewer share a context")
    ind = reviewer.get("independence")
    if not isinstance(ind, dict) or ind.get("author_context_available") is not False or ind.get("prior_exposure") != "NONE":
        raise EvidenceError("fresh independent review context not evidenced")
    return author, reviewer


def full_author(evidence, subject, root, *, contract=None):
    """Record two complete author passes; never call them independent review."""
    # Expected pins come from trusted task intake, never from the submitted report.
    binding(contract, subject)
    standard_ref = contract.get("standard_registry")
    standard = read_artifact(root, standard_ref, json_object=True)
    from sfe.standard_contract import validate as validate_standard
    try:
        validate_standard(standard)
    except (ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
        raise EvidenceError("invalid pinned Standard registry") from exc
    if standard.get("version") != "2.1.0":
        raise EvidenceError("self-check contract must be explicitly pinned to 2.1.0")
    sources = contract.get("sources")
    if not isinstance(sources, list) or not sources:
        raise EvidenceError("expected source identities absent")
    ids = set()
    for source in sources:
        if (not isinstance(source, dict) or not nonempty(source.get("source_id"))
                or not nonempty(source.get("edition")) or source["source_id"] in ids):
            raise EvidenceError("expected source identity/edition invalid or duplicate")
        ids.add(source["source_id"])
        scope(source.get("scope"))
        read_artifact(root, source.get("artifact"))
    apparatus_scope = scope(contract.get("apparatus_scope"))
    if not set(apparatus_scope).issubset(subject["scope"]):
        raise EvidenceError("apparatus scope outside subject")

    def pinned(record):
        if record.get("standard_registry") != standard_ref or record.get("sources") != sources:
            raise EvidenceError("report Standard or source identities differ from trusted task pins")

    author = report(root, evidence.get("author_report"), "AUTHOR_SELF_CHECK", subject)
    if author.get("mode") != "author_self_check" or author.get("independent") is not False:
        raise EvidenceError("explicit self-check identity required")
    pinned(author)
    passes = author.get("passes")
    if not isinstance(passes, list) or len(passes) != 2:
        raise EvidenceError("exactly two author passes required")
    previous = None
    for ref, kind in zip(passes, ("AUTHOR_MEANING", "AUTHOR_POLISH")):
        current = report(root, ref, kind, subject)
        pinned(current)
        started = timestamp(current.get("started_at"))
        completed = timestamp(current["completed_at"])
        if started > completed or (previous is not None and started < previous):
            raise EvidenceError("author passes overlap or are out of order")
        previous = completed
        if current["actor"] != author["actor"]:
            raise EvidenceError("author identity differs between passes")
        if kind == "AUTHOR_POLISH" and current.get("source_and_drafts_visible") is not False:
            raise EvidenceError("Polish pass requires reading without source and drafts")
        units = current.get("unit_checks")
        if (not isinstance(units, dict) or set(units) != set(subject["scope"])
                or not all(nonempty(value) for value in units.values())):
            raise EvidenceError("actual per-unit author assessments required")
    if previous > timestamp(author["completed_at"]):
        raise EvidenceError("author declaration precedes the two passes")
    if author.get("meaning_changes_rechecked") is not True:
        raise EvidenceError("meaning-change rechecks not declared")
    apparatus = report(root, author.get("apparatus_report"), "AUTHOR_APPARATUS", subject, partial=True)
    pinned(apparatus)
    if apparatus["actor"] != author["actor"] or apparatus["scope"] != apparatus_scope:
        raise EvidenceError("apparatus actor or expected coverage differs")
    if not previous <= timestamp(apparatus["completed_at"]) <= timestamp(author["completed_at"]):
        raise EvidenceError("apparatus must follow CORE passes and precede author declaration")
    checks = apparatus.get("unit_checks")
    if not isinstance(checks, dict) or set(checks) != {"IK", "ID", "IR"}:
        raise EvidenceError("three apparatus check scopes required")
    for units in checks.values():
        if (not isinstance(units, dict) or set(units) != set(apparatus_scope)
                or not all(nonempty(value) for value in units.values())):
            raise EvidenceError("complete actual apparatus assessments required")
    return author


def documented_r0(evidence, subject, root, axis):
    ref = evidence.get("r0")
    r0 = read_artifact(root, ref, json_object=True)
    if r0.get("schema") != "suttaflow-r0-v2" or r0.get("subject_id") != subject["subject_id"] or axis.get("r0_sha256") != ref["sha256"]:
        raise EvidenceError("R0 identity or hash differs")
    units = r0.get("units")
    if not isinstance(units, list) or not all(isinstance(u, dict) and nonempty(u.get("text")) for u in units):
        raise EvidenceError("R0 unit text absent")
    if scope([u.get("id") for u in units]) != subject["scope"]:
        raise EvidenceError("R0 does not cover the full scope")
    log = read_artifact(root, evidence.get("read_order"), json_object=True)
    if log.get("schema") != "suttaflow-read-order-v2" or log.get("subject_id") != subject["subject_id"] or log.get("complete") is not True:
        raise EvidenceError("complete read-order log absent")
    events = log.get("events")
    if not isinstance(events, list) or not events or not all(isinstance(e, dict) for e in events):
        raise EvidenceError("read-order events absent")
    valid_types = {"PALI_READ", "DICTIONARY_READ", "R0_FROZEN", "COMPARISON_READ"}
    for e in events:
        if not isinstance(e.get("type"), str) or e["type"] not in valid_types or not set(scope(e.get("scope"))).issubset(subject["scope"]):
            raise EvidenceError("unknown read event or scope")
        timestamp(e.get("at"))
    freezes = [e for e in events if e["type"] == "R0_FROZEN"]
    if len(freezes) != 1 or freezes[0].get("sha256") != ref["sha256"] or freezes[0]["scope"] != subject["scope"]:
        raise EvidenceError("unique full-scope R0 freeze event absent")
    frozen = timestamp(freezes[0]["at"])
    pali_read = {u for e in events if e["type"] == "PALI_READ" and timestamp(e["at"]) <= frozen for u in e["scope"]}
    if pali_read != set(subject["scope"]):
        raise EvidenceError("full Pali reading before R0 is not evidenced")
    if any(timestamp(e["at"]) <= frozen for e in events if e["type"] == "COMPARISON_READ"):
        raise EvidenceError("comparison was read before the R0 freeze")


def human_review(evidence, subject, root, *, partial):
    r = report(root, evidence.get("human_review"), "HUMAN_PALIST_REVIEW", subject, partial=partial)
    if r['actor'].get('kind') != 'HUMAN' or r['actor'].get('model') != 'NOT_APPLICABLE':
        raise EvidenceError('an AI model or unverified actor cannot be recorded as a human reviewer')
    verification = read_artifact(root, r.get("identity_verification"), json_object=True)
    if verification.get("kind") != "HUMAN_REVIEWER_IDENTITY" or verification.get("actor_id") != r["actor"]["id"] or not all(nonempty(verification.get(k)) for k in ("verified_by", "source_uri", "qualification")):
        raise EvidenceError("human reviewer identity and qualification not verified")
    timestamp(verification.get("verified_at"))
    return r


def hh_licence(evidence, subject, root):
    p = read_artifact(root, evidence.get("hh_licence"), json_object=True)
    binding(p, subject)
    if p.get("kind") != "LICENCE_CLEARANCE" or p.get("permission") != "GRANTED" or not all(nonempty(p.get(k)) for k in ("licensor", "source_uri", "permitted_use", "verified_by")):
        raise EvidenceError("licence clearance absent; non-monetization is not permission")
    timestamp(p.get("verified_at"))


def core_view(evidence, subject, root):
    """Bind private CORE reports to core bytes, never to later APARAT content."""
    bundle = read_artifact(root, subject.get("content"), json_object=True)
    if bundle.get("schema") != "suttaflow-publication-bundle-v2":
        raise EvidenceError("publication component manifest absent")
    for key in ("subject_id", "revision_id", "scope"):
        if bundle.get(key) != subject.get(key):
            raise EvidenceError("component manifest identity or scope differs")
    for name in ("core", "apparatus", "interpretation"):
        read_artifact(root, bundle.get(name))
    core = evidence.get("core")
    if not isinstance(core, dict) or core.get("artifact") != bundle.get("core") or core.get("scope") != subject["scope"]:
        raise EvidenceError("CORE artifact or scope differs from publication manifest")
    return {**subject, "content": core["artifact"]}
