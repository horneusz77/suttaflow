"""Scoped provenance metadata beside the unchanged DEC-03 lexical result.

The adapter verifies files, source revisions and the recorded assessment scope.
It does not infer textual independence, authenticate an assessor, change witness
counts, perform a philological review or grant any release/publication status.
See docs/standards/2.0-RC.1/SOURCE_PROVENANCE_CONTRACT_v1.md.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, cast

from . import witness_groups as G


ROLES = ("HH", "SUJATO")
STATES = ("UNKNOWN", "DEPENDENCE_RECORDED", "INDEPENDENCE_RECORDED")
RELATIONSHIP_STATES = {"DEPENDENT": STATES[1], "INDEPENDENT": STATES[2]}


class ProvenanceError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _need(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise ProvenanceError(code, message)


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _keys(value: object, expected: set[str], code: str) -> None:
    _need(isinstance(value, dict) and set(value) == expected, code,
          "required fields absent or unknown fields present")


def _json(raw: bytes) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            _need(key not in result, "DUPLICATE_JSON_KEY", "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)


def _pinned_bytes(root: Path, ref: dict) -> bytes:
    _need(isinstance(ref, dict), "ARTIFACT_REF_INVALID", "artifact reference must be an object")
    rel, expected = cast(str, ref.get("path")), ref.get("sha256")
    _need(_nonempty(rel) and not Path(rel).is_absolute() and ".." not in Path(rel).parts,
          "ARTIFACT_PATH_INVALID", "artifact path must stay inside the supplied root")
    try:
        path = (root / rel).resolve()
    except (OSError, ValueError, RuntimeError) as exc:
        raise ProvenanceError('ARTIFACT_PATH_INVALID', 'artifact path cannot be resolved') from exc
    _need(path.is_relative_to(root.resolve()), "ARTIFACT_PATH_INVALID", "artifact escapes the supplied root")
    _need(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
          "ARTIFACT_HASH_INVALID", "an exact SHA-256 pin is required")
    _need(path.is_file(), 'ARTIFACT_PATH_INVALID', 'artifact must be a regular file')
    raw = path.read_bytes()
    _need(_sha(raw) == expected, "ARTIFACT_HASH_MISMATCH", "artifact bytes differ from the recorded revision")
    return raw


def _source(root: Path, ref: dict, texts: dict) -> dict:
    _keys(ref, {"source_id", "path", "sha256", "json_pointer"}, "SOURCE_REF_INVALID")
    _need(_nonempty(ref["source_id"]), "SOURCE_REF_INVALID", "source_id is required")
    _need(ref["json_pointer"] in ("", "/translation_text"), "SOURCE_REF_INVALID", "unsupported segment selector")
    raw = _pinned_bytes(root, ref)
    parsed = _json(raw)
    if ref["json_pointer"] == "/translation_text":
        _need(isinstance(parsed, dict) and "translation_text" in parsed,
              "SOURCE_TEXT_MISMATCH", "source has no translation_text object")
        parsed = parsed["translation_text"]
    _need(isinstance(parsed, dict) and all(_nonempty(k) and isinstance(v, str) for k, v in parsed.items()),
          "SOURCE_TEXT_MISMATCH", "source is not a segment-to-text mapping")
    _need(parsed == texts, "SOURCE_TEXT_MISMATCH", "lexical input differs from the pinned source's segment texts")
    return {**copy.deepcopy(ref), "actual_sha256": _sha(raw), "binding_status": "VERIFIED"}


def _assessment(root: Path, ref: dict, source_refs: dict, hh: dict, sujato: dict, segment_ids: set[str]) -> dict:
    _keys(ref, {"path", "sha256"}, "ASSESSMENT_REF_INVALID")
    record = _json(_pinned_bytes(root, ref))
    _keys(record, {"schema", "assessment_id", "relationship", "segment_scope", "sources",
                   "basis_kind", "assessor", "assessed_at", "rationale", "support"}, "ASSESSMENT_INVALID")
    _need(record["schema"] == "suttaflow-source-provenance-assessment-v1",
          "ASSESSMENT_INVALID", "unsupported assessment schema")
    _need(_nonempty(record["assessment_id"]) and _nonempty(record["rationale"]),
          "ASSESSMENT_INVALID", "assessment ID and rationale are required")
    _need(record["relationship"] in RELATIONSHIP_STATES,
          "RELATIONSHIP_INVALID", "relationship must be explicitly recorded")
    _need(record["basis_kind"] in ("EXPLICIT_PROVENANCE_STATEMENT", "DOCUMENTED_PROVENANCE_RESEARCH"),
          "BASIS_INVALID", "lexical similarity/difference is not a provenance assessment basis")
    _keys(record["assessor"], {"id", "kind"}, "ASSESSOR_INVALID")
    _need(_nonempty(record["assessor"]["id"]) and record["assessor"]["kind"] in ("SOURCE_PUBLISHER", "HUMAN", "AI"),
          "ASSESSOR_INVALID", "attributed assessor ID and kind are required")
    _need(isinstance(record["assessed_at"], str), "ASSESSMENT_DATE_INVALID", "dated assessment required")
    at = datetime.fromisoformat(record["assessed_at"])
    _need(at.tzinfo is not None and at.utcoffset() is not None, "ASSESSMENT_DATE_INVALID", "date must include timezone")
    _need(at <= datetime.now(timezone.utc), 'ASSESSMENT_DATE_INVALID', 'future assessment cannot record a completed review')
    _need(record["sources"] == source_refs, "ASSESSMENT_SOURCE_MISMATCH", "assessment source pair/revisions/selectors differ")
    scope = record["segment_scope"]
    _need(isinstance(scope, list) and bool(scope) and all(_nonempty(k) for k in scope),
          "ASSESSMENT_SCOPE_INVALID", "explicit nonempty segment scope is required")
    _need(len(scope) == len(set(scope)) and set(scope) <= segment_ids,
          "ASSESSMENT_SCOPE_INVALID", "duplicate or foreign segment scope")
    _need(all(hh.get(k, "").strip() and sujato.get(k, "").strip() for k in scope),
          "ASSESSMENT_SCOPE_INVALID", "a relationship requires text from both pinned sources at the segment")
    support = record["support"]
    _keys(support, {"path", "sha256", "byte_start", "byte_end", "excerpt_sha256"}, "SUPPORT_INVALID")
    raw = _pinned_bytes(root, support)
    start, end = support["byte_start"], support["byte_end"]
    _need(type(start) is int and type(end) is int and 0 <= start < end <= len(raw),
          "SUPPORT_RANGE_INVALID", "support byte range is absent or outside the artifact")
    excerpt = raw[start:end]
    _need(bool(excerpt.strip()) and _sha(excerpt) == support["excerpt_sha256"],
          "SUPPORT_EXCERPT_MISMATCH", "support excerpt is empty or differs from its recorded hash")
    return {"assessment_id": record["assessment_id"], "relationship": record["relationship"],
            "segment_scope": scope, "assessment_ref": copy.deepcopy(ref),
            "basis_kind": record["basis_kind"], "assessor": record["assessor"],
            "assessed_at": record["assessed_at"], "support": support,
            "verification": "FILE_AND_SCOPE_BINDINGS_VERIFIED"}


def project_hh_sujato_provenance(root: Path, hh: dict, sujato: dict, *, source_refs: dict,
                                evidence_refs: list[dict] | tuple = ()) -> dict:
    """Project pinned, attributed records beside DEC-03, defaulting to UNKNOWN.

hh/sujato are the valid segment mappings accepted by the existing algorithm.
Malformed or missing metadata is reported in errors; it never supplies a
positive provenance state. Invalid evidence invalidates this metadata projection,
without changing the independent legacy result or becoming a count/release gate.
"""
    root = Path(root)
    legacy = G.hh_sujato_groups(hh, sujato)
    errors, sources, records = [], {}, {}

    def error(item, exc):
        errors.append({"code": getattr(exc, "code", "PROVENANCE_INPUT_INVALID"),
                       "item": item, "message": str(exc)})

    try:
        _keys(source_refs, set(ROLES), "SOURCE_PAIR_INVALID")
        for role, texts in (("HH", hh), ("SUJATO", sujato)):
            try:
                sources[role] = _source(root, source_refs[role], texts)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                sources[role] = {"binding_status": "INVALID", "supplied_ref": copy.deepcopy(source_refs[role])}
                error(role, exc)
        _need(not errors, "SOURCE_PAIR_UNVERIFIED", "both actual source files must be bound before accepting assessments")
        _need(source_refs["HH"]["source_id"] != source_refs["SUJATO"]["source_id"],
              "SOURCE_PAIR_INVALID", "the source pair must use distinct source IDs")
        _need(isinstance(evidence_refs, (list, tuple)), "ASSESSMENT_REFS_INVALID", "assessment references must be a list")
        for number, ref in enumerate(evidence_refs):
            record = _assessment(root, ref, source_refs, hh, sujato, set(legacy["segments"]))
            aid = record["assessment_id"]
            _need(aid not in records, "DUPLICATE_ASSESSMENT", "assessment IDs must be unique")
            records[aid] = record
    except (OSError, ValueError, TypeError, KeyError) as exc:
        error("projection", exc)

    segments = {}
    invalid = bool(errors)
    for sid, lexical in legacy["segments"].items():
        candidates = [r for r in records.values() if sid in r["segment_scope"]]
        relationships = {r["relationship"] for r in candidates}
        state, reason = "UNKNOWN", "NO_SCOPED_PROVENANCE_EVIDENCE"
        if invalid:
            reason = "PROVENANCE_INPUT_INVALID"
        elif len(relationships) > 1:
            reason = "CONFLICTING_PROVENANCE_ASSESSMENTS"
            errors.append({"code": reason, "item": sid, "message": "conflicting scoped records are not resolved by this adapter"})
        elif relationships:
            state = RELATIONSHIP_STATES[next(iter(relationships))]
            reason = "SCOPED_ASSESSMENT_RECORDED"
        segments[sid] = {
            "legacy_lexical_groups": copy.deepcopy(lexical),
            "source_bindings": {role: {"source_ref": role, "segment_id": sid,
                                       "text_present": bool(texts.get(sid, "").strip()),
                                       "segment_text_sha256": _sha(texts[sid].encode("utf-8")) if sid in texts else None}
                                for role, texts in (("HH", hh), ("SUJATO", sujato))},
            "provenance_assessment": {"status": state, "reason": reason,
                                      "evidence_ids": [r["assessment_id"] for r in candidates]},
        }
    return {"schema": "suttaflow-source-provenance-v1", "purpose": "METADATA_PROJECTION_ONLY",
            "validation_status": "INVALID" if errors else "VALID",
            "legacy_algorithm": "DEC-03:sfe.witness_groups.hh_sujato_groups",
            "legacy_result_sha256": _sha(json.dumps(legacy, ensure_ascii=False, sort_keys=True,
                                                    separators=(",", ":")).encode("utf-8")),
            "sources": sources, "assessments": records, "segments": segments,
            "provenance_counts": {state: sum(row["provenance_assessment"]["status"] == state for row in segments.values())
                                  for state in STATES},
            "errors": errors,
            "limitations": ["Lexical identity/difference and global similarity notes do not establish provenance.",
                            "Recorded assessments are attributed input, not authenticated identities or a new philological review.",
                            "Provenance states never alter DEC-03 group counts or grant readiness/publication permission."]}


def from_captures(root: Path, capdir: Path, hh: dict, sujato: dict, latest: dict,
                  *, evidence_manifest: Path | None = None) -> dict:
    """QA adapter for actual HH/Sujato captures and an optional separate ledger.

An absent ledger is ordinary UNKNOWN. No historical record is migrated or used
as scoped evidence; in particular dependency_note is never consumed here.
"""
    root, capdir = Path(root), Path(capdir)
    refs = {}
    for role, source_id, filename, pointer in (
            ("HH", "hh_mn41_tr", "hh_mn41_tr.json", ""),
            ("SUJATO", "en_sujato_dep", "en_sujato_dep.bin", "/translation_text")):
        refs[role] = {"source_id": source_id, "path": (capdir / filename).relative_to(root).as_posix(),
                      "sha256": latest.get(source_id, {}).get("sha256"), "json_pointer": pointer}
    evidence_refs, manifest_error = [], None
    manifest_binding = None
    if evidence_manifest is not None and evidence_manifest.exists():
        try:
            _need(evidence_manifest.resolve().is_relative_to(root.resolve()),
                  "LEDGER_INVALID", "provenance ledger must stay inside the supplied root")
            raw = evidence_manifest.read_bytes()
            ledger = _json(raw)
            _keys(ledger, {"schema", "assessments"}, "LEDGER_INVALID")
            _need(ledger["schema"] == "suttaflow-source-provenance-ledger-v1", "LEDGER_INVALID", "unknown provenance ledger")
            evidence_refs = ledger["assessments"]
            manifest_binding = {"path": evidence_manifest.relative_to(root).as_posix(), "sha256": _sha(raw)}
        except (OSError, ValueError, TypeError, KeyError) as exc:
            manifest_error = {"code": "LEDGER_INVALID", "item": "evidence_manifest", "message": str(exc)}
            evidence_refs = []
    result = project_hh_sujato_provenance(root, hh, sujato, source_refs=refs, evidence_refs=evidence_refs)
    result["evidence_manifest"] = manifest_binding
    if manifest_error:
        result["validation_status"] = "INVALID"
        result["errors"].append(manifest_error)
        for row in result["segments"].values():
            row["provenance_assessment"]["reason"] = "PROVENANCE_INPUT_INVALID"
    return result
