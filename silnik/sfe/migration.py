"""Deterministic, local-only migration sidecars (SF-RULE-MIG-001 / STA-005).

This module does not write source documents, status axes, consents or a queue.
It preserves complete source bytes, records what is actually present, proposes
reference substitutions, and writes only new files in a caller-owned directory.
Its result is never certification or permission to publish. A trusted receipt
records which files this invocation created; identical files found without it
remain unowned. The caller must preserve receipt origin and integrity: matching
plain JSON is not authenticated proof of ownership. Use a private output
directory without concurrent writers. Remote revision CAS is outside this dry-run.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

from .status_axes import ALLOWED


class MigrationError(ValueError):
    """An invalid pin, ambiguous input or unsafe output blocks a migration."""

    receipt: dict[str, object] | None = None


def _bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _load(data):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise MigrationError("JSON_DUPLICATE_KEY: " + key)
            out[key] = value
        return out

    try:
        return json.loads(data, object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              MigrationError("JSON_NONFINITE: " + value)))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise MigrationError("JSON_INVALID: " + str(exc)) from exc


def _pointer(value, pointer):
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise MigrationError("REVISION_POINTER_INVALID")
    try:
        for key in pointer[1:].split("/"):
            key = key.replace("~1", "/").replace("~0", "~")
            value = value[int(key)] if isinstance(value, list) else value[key]
        return value
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise MigrationError("REVISION_POINTER_MISSING: " + pointer) from exc


def _read_hash(path, expected, label):
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise MigrationError(label + "_HASH_PIN_INVALID")
    if not isinstance(path, str) or not Path(path).is_absolute():
        raise MigrationError(label + "_PATH_MUST_BE_ABSOLUTE")
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise MigrationError(label + "_UNREADABLE: " + str(exc)) from exc
    if _sha(data) != expected:
        raise MigrationError(label + "_HASH_MISMATCH: " + path)
    return data


def _preflight_source(source):
    if not isinstance(source, dict):
        raise MigrationError("SOURCE_INVALID")
    for name in ("key", "kind", "path", "expected_sha256", "metadata_path",
                 "metadata_sha256", "source_id", "id_pointer", "revision_id", "revision_pointer"):
        if not isinstance(source.get(name), str) or not source[name].strip():
            raise MigrationError("SOURCE_FIELD_INVALID: " + name)
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", source["key"]):
        raise MigrationError("SOURCE_KEY_INVALID")
    if source["kind"] not in {"QUEUE", "LOG", "STATUS_AXES_V1"}:
        raise MigrationError("SOURCE_KIND_INVALID")
    data = _read_hash(source["path"], source["expected_sha256"], "SOURCE")
    metadata = _load(_read_hash(source["metadata_path"], source["metadata_sha256"], "METADATA"))
    if _pointer(metadata, source["id_pointer"]) != source["source_id"]:
        raise MigrationError("SOURCE_ID_MISMATCH")
    if _pointer(metadata, source["revision_pointer"]) != source["revision_id"]:
        raise MigrationError("REVISION_MISMATCH")
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise MigrationError("SOURCE_UTF8_REQUIRED") from exc
    ranges = source.get("operative_line_ranges", [])
    if not isinstance(ranges, list):
        raise MigrationError("OPERATIVE_RANGES_INVALID")
    for pair in ranges:
        if (not isinstance(pair, list) or len(pair) != 2
                or any(type(x) is not int for x in pair)
                or not (1 <= pair[0] <= pair[1] <= len(text.splitlines()))):
            raise MigrationError("OPERATIVE_RANGES_INVALID")
    return data, text


_REF = re.compile(
    r"(?:SuttaFlow\s+)?Standard(?:u|zie)?\s*,?\s*(?:sekcj(?:a|e|i)|§{1,2})\s*"
    r"(?P<first>16|18)(?:\s*(?:i|oraz|,|/)\s*(?:§\s*)?(?P<second>16|18))?\b",
    re.IGNORECASE,
)
_ROW = re.compile(
    r"^(?P<status>NEXT|ACTIVE|BLOCKED|QUEUED|DONE|SKIPPED)\s*[·|]\s*"
    r"(?P<subject>(?:MN|DN|AN|SN|Dhp|Ud|Iti|Snp|Thag|Thig|Ja)\s*\d+(?:[.\-–]\d+)*)"
    r"(?=\s*[·|—]|\s*$).*$", re.MULTILINE,
)


def _location(text, start, end):
    return {"char_start": start, "char_end": end,
            "byte_start": len(text[:start].encode("utf-8")),
            "byte_end": len(text[:end].encode("utf-8")),
            "line": text.count("\n", 0, start) + 1}


def _references(text, source, crosswalk):
    result = []
    for match in _REF.finditer(text):
        sections = list(dict.fromkeys(v for v in match.group("first", "second") if v))
        loc = _location(text, match.start(), match.end())
        active = any(lo <= loc["line"] <= hi for lo, hi in source.get("operative_line_ranges", []))
        rules = sorted({rule for section in sections for rule in crosswalk[section]["rule_ids"]})
        result.append({"source_key": source["key"], **loc,
                       "raw_reference": match.group(), "old_sections": sections,
                       "rule_ids": rules, "basis": {s: crosswalk[s] for s in sections},
                       "disposition": "PROPOSE_REFERENCE_ONLY" if active else "HISTORICAL_REFERENCE_RETAINED",
                       "proposed_reference": "; ".join(rules) if active else match.group(),
                       "activation_status": "NOT_ACTIVATED"})
    return result


def _observations(text, source):
    return [{"source_key": source["key"], "source_kind": source["kind"],
             "subject_id": re.sub(r"\s+", "", m["subject"]).lower().replace("–", "-"),
             "raw_subject": m["subject"], "raw_status": m["status"], "raw_line": m.group(),
             **_location(text, m.start(), m.end())} for m in _ROW.finditer(text)]


def _knowledge(raw):
    result = {}
    for axis in "ABCDE":
        present = axis in raw
        field = raw.get(axis)
        value = field.get("value") if isinstance(field, dict) else field
        if not present or field is None or (isinstance(field, dict) and (
                "value" not in field or value is None or (isinstance(value, str) and not value.strip()))):
            state, reason = "UNKNOWN", "SUBSTANTIVE_VALUE_NOT_RECORDED"
        elif not isinstance(field, dict) or not isinstance(value, str) or value not in ALLOWED[axis]:
            state, reason = "UNRESOLVED", "PRESENT_VALUE_OUTSIDE_NATIVE_V1_CONTRACT"
        else:
            state, reason = "RECORDED", "HISTORICAL_ASSERTION_PRESERVED_WITHOUT_RECERTIFICATION"
        result[axis] = {"knowledge_state": state, "raw_present": present,
                        "raw_value": value, "source_pointer": "/" + axis,
                        "proposed_native_value": value if state == "RECORDED" else None,
                        "native_write": False, "reason": reason}
    return result


def make_plan(sources, section_crosswalk):
    """Read pinned snapshots and propose sidecars. This function does not write.

    ``operative_line_ranges`` is explicit curator input, never inferred from a
    keyword. References outside those reviewed ranges remain historical text.
    Queue/log parsing covers explicit status rows only; narrative history stays
    intact and is not silently converted to present-day axis values.
    """
    if not isinstance(sources, list) or not sources:
        raise MigrationError("SOURCES_REQUIRED")
    sources = copy.deepcopy(sources)
    crosswalk = copy.deepcopy(section_crosswalk)
    if not isinstance(crosswalk, dict) or set(crosswalk) != {"16", "18"}:
        raise MigrationError("CROSSWALK_SECTIONS_REQUIRED")
    for section, entry in crosswalk.items():
        if (not isinstance(entry, dict) or not isinstance(entry.get("rule_ids"), list)
                or not entry["rule_ids"] or not entry.get("basis")
                or any(not isinstance(rule, str) or not re.fullmatch(r"SF-RULE-[A-Z]+-\d{3}", rule)
                       for rule in entry["rule_ids"])):
            raise MigrationError("CROSSWALK_INVALID: " + section)
    verified = [(source, *_preflight_source(source)) for source in sources]
    if len({s["key"] for s, _, _ in verified}) != len(sources):
        raise MigrationError("SOURCE_KEY_DUPLICATE")
    verified.sort(key=lambda entry: entry[0]["key"])
    results = []
    for source, data, text in verified:
        result = {"source_key": source["key"], "kind": source["kind"],
                  "raw_original": {"sha256": _sha(data), "bytes": len(data),
                                   "base64": base64.b64encode(data).decode("ascii")},
                  "new_certification": "NOT_EVALUATED", "native_write": False,
                  "activation_status": "NOT_ACTIVATED", "reference_proposals": [],
                  "explicit_status_rows": []}
        if source["kind"] == "STATUS_AXES_V1":
            raw = _load(data)
            if not isinstance(raw, dict) or raw.get("schema") != "suttaflow-status-axes-v1":
                raise MigrationError("STATUS_AXES_SCHEMA_REQUIRED")
            result.update(raw_json=raw, knowledge=_knowledge(raw))
        else:
            result.update(raw_text=text, knowledge={"document": {
                "knowledge_state": "RECORDED", "raw_present": True,
                "reason": "COMPLETE_PINNED_DOCUMENT_PRESERVED"}},
                narrative_axis_projection="NOT_PERFORMED",
                reference_proposals=_references(text, source, crosswalk),
                explicit_status_rows=_observations(text, source))
        results.append(result)
    rows = [row for result in results for row in result["explicit_status_rows"]]
    conflicts = [{"code": "QUEUE_LOG_SCOPE_REQUIRES_RECONCILIATION", "subject_id": q["subject_id"],
                  "queue": q, "log": log,
                  "reason": "A historical completion and a queued scope need explicit version/scope reconciliation."}
                 for q in rows if q["source_kind"] == "QUEUE" and q["raw_status"] in {"NEXT", "ACTIVE", "BLOCKED", "QUEUED"}
                 for log in rows if log["source_kind"] == "LOG" and log["raw_status"] == "DONE"
                 and q["subject_id"] == log["subject_id"]]
    plan = {"schema": "suttaflow-migration-plan-v1", "mode": "DRY_RUN_ONLY",
            "sources": [source for source, _, _ in verified], "section_crosswalk": crosswalk,
            "results": results, "conflicts": conflicts,
            "source_mutations_permitted": False, "publication_authorized": False}
    plan["plan_id"] = _sha(_bytes(plan))
    return plan


def _check_plan(plan):
    if not isinstance(plan, dict) or plan.get("schema") != "suttaflow-migration-plan-v1":
        raise MigrationError("PLAN_SCHEMA_INVALID")
    body = {key: value for key, value in plan.items() if key != "plan_id"}
    if plan.get("plan_id") != _sha(_bytes(body)):
        raise MigrationError("PLAN_HASH_MISMATCH")
    if (plan.get("mode") != "DRY_RUN_ONLY" or plan.get("source_mutations_permitted") is not False
            or plan.get("publication_authorized") is not False):
        raise MigrationError("PLAN_MODE_INVALID")


def artifacts(plan):
    """Return deterministic names and bytes without performing filesystem writes."""
    _check_plan(plan)
    pins = {source["key"]: source for source in plan["sources"]}
    result = []
    for entry in plan["results"]:
        key = entry["source_key"]
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", key) or key not in pins:
            raise MigrationError("PLAN_SOURCE_KEY_INVALID")
        data = _bytes({"schema": "suttaflow-migration-sidecar-v1", "plan_id": plan["plan_id"],
                       "source_pin": pins[key], "result": entry})
        result.append({"filename": key + ".migration-" + plan["plan_id"][:16] + ".json",
                       "bytes": data, "sha256": _sha(data)})
    return result


def _redirects_path(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _safe_directory(path):
    path = Path(os.path.abspath(path))
    for component in (path, *path.parents):
        if _redirects_path(component):
            raise MigrationError("OUTPUT_SYMLINK_REFUSED: " + str(component))
        if component.exists() and not component.is_dir():
            raise MigrationError("OUTPUT_DIRECTORY_REQUIRED")
    return path


def _existing(path, expected, code):
    if _redirects_path(path):
        raise MigrationError("OUTPUT_SYMLINK_REFUSED: " + str(path))
    if path.exists():
        if not path.is_file() or _sha(path.read_bytes()) != expected:
            raise MigrationError(code + ": " + str(path))
        return True
    return False


def _receipt(plan, output, receipt, expected):
    if receipt is None:
        return {"schema": "suttaflow-migration-receipt-v1", "plan_id": plan["plan_id"],
                "output_directory": str(output), "created": [], "already_present": [],
                "remaining": [], "completed": False}
    receipt = copy.deepcopy(receipt)
    if (not isinstance(receipt, dict) or receipt.get("schema") != "suttaflow-migration-receipt-v1"
            or receipt.get("plan_id") != plan["plan_id"] or receipt.get("output_directory") != str(output)
            or not isinstance(receipt.get("created"), list)):
        raise MigrationError("RECEIPT_INVALID")
    seen = set()
    for entry in receipt["created"]:
        if (not isinstance(entry, dict) or not isinstance(entry.get("filename"), str) or entry["filename"] not in expected
                or entry.get("sha256") != expected[entry["filename"]]
                or entry["filename"] in seen):
            raise MigrationError("RECEIPT_OWNERSHIP_INVALID")
        seen.add(entry["filename"])
    return receipt


def _create_atomic(path, data):
    """Publish one complete file exclusively; never replace an existing target."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".migration-", suffix=".tmp", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path, follow_symlinks=False)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def apply_plan(plan, output_directory, *, batch_size=None, receipt=None):
    """Create new sidecars, optionally in bounded batches for durable checkpoints.

    Serialize the returned receipt between batches. Repeating without a receipt
    is still idempotent, but cannot claim ownership of previously present files.
    Supplied receipts must have trusted origin and integrity; they are not signed.
    All source and target preflights run before the first write in every batch.
    """
    _check_plan(plan)
    if plan.get("conflicts"):
        raise MigrationError("QUEUE_LOG_CONFLICT_UNRESOLVED")
    if batch_size is not None and (type(batch_size) is not int or batch_size < 1):
        raise MigrationError("BATCH_SIZE_INVALID")
    # Rebuild from pinned bytes to catch altered proposals as well as stale inputs.
    if make_plan(plan["sources"], plan["section_crosswalk"]) != plan:
        raise MigrationError("PLAN_PROPOSAL_MISMATCH")
    output = _safe_directory(output_directory)
    pending = artifacts(plan)
    expected = {entry["filename"]: entry["sha256"] for entry in pending}
    result = _receipt(plan, output, receipt, expected)
    owned = {entry["filename"] for entry in result["created"]}
    present = {entry["filename"]: _existing(output / entry["filename"], entry["sha256"], "EXISTING_FILE_CONFLICT")
               for entry in pending}
    if any(not present[name] for name in owned):
        raise MigrationError("RECEIPT_CREATED_FILE_MISSING")
    result["already_present"] = [{"filename": name, "sha256": expected[name]}
                                 for name, exists in present.items() if exists and name not in owned]
    output.mkdir(parents=True, exist_ok=True)
    made = 0
    for entry in pending:
        if present[entry["filename"]] or (batch_size is not None and made >= batch_size):
            continue
        try:
            _create_atomic(output / entry["filename"], entry["bytes"])
        except OSError as exc:
            error = MigrationError("EXCLUSIVE_CREATE_FAILED: " + str(exc))
            error.receipt = result
            raise error from exc
        if not _existing(output / entry["filename"], entry["sha256"], "WRITE_READBACK_FAILED"):
            raise MigrationError("WRITE_READBACK_MISSING")
        result["created"].append({"filename": entry["filename"], "sha256": entry["sha256"]})
        present[entry["filename"]] = True
        made += 1
    result["remaining"] = [name for name, exists in present.items() if not exists]
    result["completed"] = not result["remaining"]
    return result


def _rollback_receipt(plan, output, created, progress):
    """Bind an append-only deletion prefix to the exact trusted creation receipt."""
    binding = _sha(_bytes(created))
    if progress is None:
        return {"schema": "suttaflow-migration-rollback-v1", "plan_id": plan["plan_id"],
                "output_directory": str(output), "creation_receipt_sha256": binding,
                "removed": [], "remaining": [entry["filename"] for entry in created["created"]],
                "completed": not created["created"], "source_mutations": 0}
    result = copy.deepcopy(progress)
    if (not isinstance(result, dict) or result.get("schema") != "suttaflow-migration-rollback-v1"
            or result.get("plan_id") != plan["plan_id"] or result.get("output_directory") != str(output)
            or result.get("creation_receipt_sha256") != binding or not isinstance(result.get("removed"), list)
            or len(result["removed"]) > len(created["created"])
            or result["removed"] != created["created"][:len(result["removed"])]):
        raise MigrationError("ROLLBACK_RECEIPT_INVALID")
    remaining = [entry["filename"] for entry in created["created"][len(result["removed"]):]]
    if (result.get("remaining") != remaining or type(result.get("completed")) is not bool
            or result["completed"] != (not remaining) or type(result.get("source_mutations")) is not int
            or result["source_mutations"] != 0):
        raise MigrationError("ROLLBACK_RECEIPT_INVALID")
    return result


def rollback(plan, output_directory, receipt, *, progress=None):
    """Remove identical new sidecars named by a trusted creation receipt.

    Source bytes are never targets. With a genuine unaltered receipt, pre-existing
    identical files remain unowned. A forged matching receipt could falsely claim
    them; the caller, not this plain-JSON protocol, authenticates receipt ownership.
    Every still-owned file is checked before any deletion; changed files block
    the whole batch. A controlled failure carries genuine progress in
    ``MigrationError.receipt``. Persist it and resume with the same creation
    receipt and ``progress=...``. Only a successful unlink appends to ``removed``;
    an unexplained missing file never counts as our deletion. A recorded removed
    name that reappears is also refused, even with identical bytes. Progress has
    the same trusted-origin requirement as the original creation receipt.
    Use the private directory without concurrent writers. A hard process loss
    before progress is preserved cannot safely infer an undocumented deletion.
    """
    _check_plan(plan)
    output = _safe_directory(output_directory)
    expected = {entry["filename"]: entry["sha256"] for entry in artifacts(plan)}
    checked = _receipt(plan, output, receipt, expected)
    result = _rollback_receipt(plan, output, checked, progress)
    pending = checked["created"][len(result["removed"]):]
    try:
        for entry in result["removed"]:
            path = output / entry["filename"]
            if path.exists() or path.is_symlink():
                raise MigrationError("ROLLBACK_REMOVED_FILE_REAPPEARED: " + str(path))
        for entry in pending:
            if not _existing(output / entry["filename"], entry["sha256"], "ROLLBACK_CHANGED_FILE"):
                raise MigrationError("ROLLBACK_MISSING_FILE: " + entry["filename"])
        for entry in pending:
            path = output / entry["filename"]
            if not _existing(path, entry["sha256"], "ROLLBACK_CHANGED_FILE"):
                raise MigrationError("ROLLBACK_MISSING_FILE: " + entry["filename"])
            try:
                path.unlink()
            except OSError as exc:
                raise MigrationError("ROLLBACK_UNLINK_FAILED: " + str(path) + ": " + str(exc)) from exc
            result["removed"].append(copy.deepcopy(entry))
            result["remaining"] = result["remaining"][1:]
            result["completed"] = not result["remaining"]
    except MigrationError as exc:
        exc.receipt = copy.deepcopy(result)
        raise
    except OSError as exc:
        error = MigrationError("ROLLBACK_IO_FAILED: " + str(exc))
        error.receipt = copy.deepcopy(result)
        raise error from exc
    return result
