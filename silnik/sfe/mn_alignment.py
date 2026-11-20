"""Generic MN segmentation and mechanical Pali ↔ Polish relations (D4).

Inputs are explicit, locally captured and SHA-256 pinned. Bilara JSON strings
retain their native segment IDs and raw JSON-string byte ranges. Polish UTF-8
sections use [§N] / [§colophon] markers and source byte ranges. Metadata is kept.
Repeated formulas are checked per declared instance and against every occurrence
of their declared Pali anchor. This does not identify all formulas linguistically.

ALIGNED means mechanical completeness only. This module neither translates nor
grants Pali-first provenance, philological review or publication permission.
The historical MN41 carrier/formula adapter in sfe.align remains unchanged.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from . import align
from . import witness


class InputError(ValueError):
    def __init__(self, code: str, message: str = ""):
        self.code = code
        super().__init__(code + (": " + message if message else ""))


def _sutta(value):
    if not isinstance(value, str) or not re.fullmatch(r"mn[1-9][0-9]*", value):
        raise InputError("SUTTA_ID_INVALID")
    return value


def _decode(raw: bytes, side: str):
    try:
        return raw.decode("utf-8")
    except UnicodeError as exc:
        raise InputError(side + "_ENCODING_INVALID") from exc


def pali_segments(raw: bytes, sutta_id: str) -> list[dict]:
    """Parse all Bilara segment strings without losing duplicate keys or bytes.

byte_start/end delimit the complete JSON string token, including quotes and any
escapes; json.loads(raw[start:end]) is exactly the recorded text. No header,
colophon, whitespace inside a string, or segment is silently discarded.
"""
    _sutta(sutta_id)
    text = _decode(raw, "PALI")
    offsets = witness.byte_offsets(text)
    decoder = json.JSONDecoder()
    units, seen = [], set()

    def whitespace(index):
        while index < len(text) and text[index] in " \r\n\t":
            index += 1
        return index

    try:
        position = whitespace(0)
        if position == len(text) or text[position] != "{":
            raise InputError("PALI_JSON_INVALID", "expected an object")
        position = whitespace(position + 1)
        if position < len(text) and text[position] == "}":
            raise InputError("PALI_UNITS_EMPTY")
        while True:
            identifier, position = decoder.raw_decode(text, position)
            if not align._identifier(identifier):
                raise InputError("PALI_UNIT_ID_INVALID")
            if not identifier.startswith(sutta_id + ":") or identifier == sutta_id + ":":
                raise InputError("PALI_SUTTA_MISMATCH", identifier)
            if identifier in seen:
                raise InputError("PALI_DUPLICATE_ID", identifier)
            seen.add(identifier)
            position = whitespace(position)
            if position >= len(text) or text[position] != ":":
                raise InputError("PALI_JSON_INVALID", "missing colon")
            begin = whitespace(position + 1)
            value, end = decoder.raw_decode(text, begin)
            if not isinstance(value, str) or not value.strip():
                raise InputError("PALI_UNIT_TEXT_INVALID", identifier)
            units.append({"id": identifier, "text": value,
                "kind": "METADATA" if identifier.startswith(sutta_id + ":0.") else "BODY",
                "byte_start": offsets[begin], "byte_end": offsets[end], "locator_kind": "JSON_STRING"})
            position = whitespace(end)
            if position < len(text) and text[position] == "}":
                position = whitespace(position + 1)
                break
            if position >= len(text) or text[position] != ",":
                raise InputError("PALI_JSON_INVALID", "missing comma or closing brace")
            position = whitespace(position + 1)
        if position != len(text):
            raise InputError("PALI_JSON_INVALID", "trailing content")
    except json.JSONDecodeError as exc:
        raise InputError("PALI_JSON_INVALID", str(exc)) from exc
    return units


SECTION = re.compile(r"\[§([0-9]+|colophon)\][ \t]*")
SENTENCE = re.compile(r'(?<=[.?!])(?P<closing>[”»"]*)(?P<space>[ \t]+)(?=[A-ZĄĆĘŁŃÓŚŹŻ„«—–])')


def polish_segments(raw: bytes, sutta_id: str) -> list[dict]:
    """Segment explicitly marked UTF-8 Polish core text for any MN.

Every nonblank character is retained in a unit or an explicit section marker.
No title/colophon words are guessed. The caller supplies core text with all its
section markers; this adapter is not a whole-document editorial formatter.
"""
    _sutta(sutta_id)
    text = _decode(raw, "PL")
    offsets = witness.byte_offsets(text)
    units: list[dict] = []
    counts: Counter[str] = Counter()
    section, line_start = None, 0
    for line in text.splitlines(keepends=True):
        start = line_start + len(line) - len(line.lstrip())
        end = line_start + len(line.rstrip())
        line_start += len(line)
        if start >= end:
            continue
        marker = SECTION.match(text, start)
        if marker:
            section = marker.group(1)
            start = marker.end()
        elif text.startswith("[§", start):
            raise InputError("PL_SECTION_INVALID")
        if section is None:
            raise InputError("PL_SECTION_MISSING")
        spans = []
        cursor = start
        for boundary in SENTENCE.finditer(text, start, end):
            spans.append((cursor, boundary.start("space")))
            cursor = boundary.end()
        spans.append((cursor, end))
        for first, last in spans:
            while first < last and text[first].isspace():
                first += 1
            while last > first and text[last - 1].isspace():
                last -= 1
            if first == last:
                continue
            counts[section] += 1
            units.append({"id": f"pl.{sutta_id}.§{section}.{counts[section]}",
                "section": section, "text": text[first:last],
                "byte_start": offsets[first], "byte_end": offsets[last], "locator_kind": "UTF8_TEXT"})
    if not units:
        raise InputError("PL_UNITS_EMPTY")
    return units


def formula_checks(pali, polish, groups, rules):
    """Check each declared formula instance, with an exhaustive literal anchor.

The anchor must occur once in each listed group and wholly inside one source
segment. Every source occurrence must be accounted for by exactly one group.
Checks are literal NFC/casefold comparisons, not a judgment of translation.
"""
    problems, checked, seen = [], 0, set()
    by_group = {group.get("id"): group for group in groups if align._identifier(group.get("id"))}
    by_pali = {unit["id"]: unit["text"] for unit in pali}
    by_polish = {unit["id"]: unit["text"] for unit in polish}

    def bad(code, rule, **extra):
        problems.append({"code": code, "rule": rule, **extra})

    if not isinstance(rules, list):
        bad("FORMULA_RULES_INVALID", "formula_rules")
        rules = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict) or not align._identifier(rule.get("id")):
            bad("FORMULA_RULE_INVALID", index)
            continue
        identifier = rule["id"]
        if identifier in seen:
            bad("FORMULA_RULE_DUPLICATE_ID", identifier)
        seen.add(identifier)
        anchor = rule.get("pali_anchor")
        fields = [rule.get(key) for key in ("pali_contains", "pl_contains", "group_ids")]
        if not isinstance(anchor, str) or not anchor.strip() \
                or any(not isinstance(values, list) or not values
                       or any(not isinstance(value, str) or not value.strip() for value in values)
                       or len(set(values)) != len(values) for values in fields):
            bad("FORMULA_RULE_INVALID", identifier)
            continue
        needle = witness.compare_key(anchor)
        expected = Counter({uid: witness.compare_key(text).count(needle)
                            for uid, text in by_pali.items() if needle in witness.compare_key(text)})
        covered: Counter[str] = Counter()
        for gid in rule["group_ids"]:
            group = by_group.get(gid)
            if group is None:
                bad("FORMULA_GROUP_UNKNOWN", identifier, group=gid)
                continue
            ptext = witness.compare_key(" ".join(by_pali.get(uid, "") for uid in group["pali"]))
            ltext = witness.compare_key(" ".join(by_polish.get(uid, "") for uid in group["pl"]))
            hits = [uid for uid in group["pali"] if needle in witness.compare_key(by_pali.get(uid, ""))]
            covered.update(hits)
            checked += 1
            failed = []
            if ptext.count(needle) != 1 or len(hits) != 1:
                failed.append("pali_anchor_occurrence_count")
            failed += ["pali_contains:" + phrase for phrase in rule["pali_contains"] if witness.compare_key(phrase) not in ptext]
            failed += ["pl_contains:" + phrase for phrase in rule["pl_contains"] if witness.compare_key(phrase) not in ltext]
            if failed:
                bad("FORMULA_INSTANCE_FAILED", identifier, group=gid, failed=failed)
        if not expected or expected != covered:
            bad("FORMULA_OCCURRENCES_UNACCOUNTED", identifier,
                missing=list((expected - covered).elements()), extra=list((covered - expected).elements()))
    return problems, {"rules_declared": len(rules), "instances_checked": checked,
                      "formula_identification": "NOT_ESTABLISHED_BY_TOOL"}


def _path(root, relative, label):
    if not isinstance(relative, str) or not relative.strip() or "\0" in relative or Path(relative).is_absolute():
        raise InputError(label + "_PATH_INVALID")
    path = root / relative
    try:
        contained = root.resolve() in path.resolve().parents
    except (OSError, ValueError, RuntimeError) as exc:
        raise InputError(label + "_PATH_INVALID", str(exc)) from exc
    if not contained:
        raise InputError(label + "_PATH_INVALID")
    if not path.is_file():
        raise InputError(label + ("_SOURCE_MISSING" if label in {"PALI", "PL"} else "_MISSING"))
    return path


def _pinned_bytes(root, spec, label):
    if not isinstance(spec, dict):
        raise InputError(label + "_SPEC_INVALID")
    pin = spec.get("sha256")
    if not isinstance(pin, str) or not re.fullmatch(r"[0-9a-f]{64}", pin):
        raise InputError(label + "_PIN_INVALID")
    path = _path(root, spec.get("path"), label)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin:
        raise InputError(label + "_HASH_MISMATCH")
    return raw


def _json(raw, label):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InputError(label + "_DUPLICATE_KEY", key)
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=unique)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise InputError(label + "_JSON_INVALID") from exc


def build(root: Path, manifest: dict) -> dict:
    """Evaluate a pinned generic MN input manifest without writing any input."""
    root = Path(root)
    problems: list[dict] = []
    units: dict[str, list[dict] | None] = {"pali": None, "pl": None}
    mapping: dict = {"groups": []}
    sutta, test_only = None, False

    def record(exc):
        problems.append({"code": exc.code if isinstance(exc, InputError) else "INPUT_UNREADABLE", "msg": str(exc)})

    try:
        if not isinstance(manifest, dict) or manifest.get("schema") != "suttaflow-mn-alignment-input-v1":
            raise InputError("MANIFEST_SCHEMA_INVALID")
        sutta = _sutta(manifest.get("sutta_id"))
        test_only = manifest.get("test_only", False)
        if type(test_only) is not bool:
            raise InputError("MANIFEST_TEST_ONLY_INVALID")
    except InputError as exc:
        record(exc)
    if not problems and sutta is not None:
        for side, format_name, parser in (("pali", "BILARA_JSON", pali_segments), ("pl", "UTF8_SECTIONS", polish_segments)):
            try:
                spec = manifest.get(side)
                if not isinstance(spec, dict) or spec.get("format") != format_name:
                    raise InputError(side.upper() + "_FORMAT_INVALID")
                units[side] = parser(_pinned_bytes(root, spec, side.upper()), sutta)
            except (InputError, OSError) as exc:
                record(exc)
        try:
            mapping = _json(_pinned_bytes(root, manifest.get("mapping"), "MAPPING"), "MAPPING")
            if not isinstance(mapping, dict) or mapping.get("sutta_id") != sutta or not isinstance(mapping.get("groups"), list):
                raise InputError("MAPPING_SCHEMA_INVALID")
        except (InputError, OSError) as exc:
            record(exc)
            mapping = {"groups": []}
    result = align.validate_groups(units["pali"] or [], units["pl"] or [], mapping["groups"])
    checks = {"rules_declared": None, "instances_checked": None, "formula_identification": "NOT_ESTABLISHED_BY_TOOL"}
    if not problems:
        formula_problems, checks = formula_checks(units["pali"], units["pl"], result["groups_detail"], mapping.get("formula_rules", []))
        result["formula_problems"] = formula_problems
    for side in ("pali", "pl"):
        if units[side] is None:
            result[side + "_units"] = None
    result["input_problems"] = problems
    result["complete"] = result["complete"] and not problems and not result["formula_problems"]
    result.update({"schema": "suttaflow-mn-alignment-report-v1", "sutta_id": sutta,
                   "status": "ALIGNED" if result["complete"] else "HOLD", "test_only": test_only,
                   "segments": units, "formula_checks": checks, "review_status": "NOT_PERFORMED",
                   "pali_first_granted": False, "ready_for_publication": False})
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", required=True, help="Input manifest path relative to root")
    args = parser.parse_args()
    try:
        manifest = _json(_path(args.root, args.manifest, "MANIFEST").read_bytes(), "MANIFEST")
        result = build(args.root, manifest)
    except (InputError, OSError) as exc:
        result = build(args.root, {})
        result["input_problems"] = [{"code": exc.code if isinstance(exc, InputError) else "INPUT_UNREADABLE", "msg": str(exc)}]
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
