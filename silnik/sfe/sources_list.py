"""Public source list (with links) for channel descriptions, generated from evidence.

validate() separates capture integrity from recorded reading and actual use. A
capture alone is never proof of reading. The optional source-readings-v1 ledger
binds the reader, time, used range and use references to the captured SHA-256.
The ledger records an attestation; it does not authenticate the reader's identity.
render() is a pure historical formatter and grants no validation status.
check_links() records HTTP status for every public URL (run before publishing).
"""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.request
from pathlib import Path
from typing import Any, TypeGuard

REQUIRED_ROLES = {"PALI_BASE", "PALI_WITNESS", "HH_EN", "BODHI_EN", "THANISSARO_EN",
                  "COMMENTARY", "CANONICAL_GLOSS", "DEPENDENCY_PROBE_ONLY", "SUJATO_EN"}


def _nonempty(value) -> TypeGuard[str]:
    return isinstance(value, str) and bool(value.strip())


def _lexicon_identity(value: str) -> str:
    """Known names, never arbitrary prefix matches such as D -> DPD."""
    if re.fullmatch(r"DPD(?: v[0-9]+\.[0-9]+\.[0-9]{8})?", value):
        return "DPD"
    if value in {"PTS PED", "PTS PED (DSAL)"}:
        return "PTS PED"
    return value


def _reading_valid(record: dict, capture: dict) -> bool:
    if record.get("status") != "READ" or capture.get("status") != "CAPTURED":
        return False
    if capture.get("read_status") is not None and not isinstance(capture["read_status"], str):
        return False
    if capture.get("read_status") in ("NIE_ODCZYTANO", "NOT_READ", "UNREAD"):
        return False
    digest = record.get("source_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest) or digest != capture.get("sha256"):
        return False
    if not _nonempty(record.get("reader_id")):
        return False
    uses = record.get("used_in")
    if not isinstance(uses, list) or not uses or any(not _nonempty(item) for item in uses) or len(set(uses)) != len(uses):
        return False
    scope = record.get("scope")
    if not isinstance(scope, dict) or scope.get("kind") != "BYTE_RANGE":
        return False
    start, end, size = scope.get("start"), scope.get("end"), capture.get("bytes")
    if type(start) is not int or type(end) is not int or type(size) is not int:
        return False
    if not 0 <= start < end <= size:
        return False
    try:
        stamp = dt.datetime.fromisoformat(record["read_at_utc"])
        if stamp.tzinfo is None or stamp > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
            return False
    except (KeyError, TypeError, ValueError):
        return False
    return True


def validate(src: dict, capture_log: list[dict], decisions: dict, *, read_ledger: dict | None = None) -> list[dict]:
    probs: list[dict] = []
    if not isinstance(src, dict) or not isinstance(src.get("items"), list) or not isinstance(src.get("groups"), list) \
            or not isinstance(capture_log, list) or not isinstance(decisions, dict):
        return [{"code": "SOURCE_LIST_INVALID", "item": "inputs"}]
    latest = {}
    for record in capture_log:
        if not isinstance(record, dict) or not _nonempty(record.get("id")):
            probs.append({"code": "SOURCE_CAPTURE_RECORD_INVALID", "item": "capture_log"})
            continue
        if record["id"] in latest:
            probs.append({"code": "SOURCE_CAPTURE_DUPLICATE_ID", "item": record["id"]})
        latest[record["id"]] = record
    readings = decisions.get("source_readings", [])
    if read_ledger is not None:
        if not isinstance(read_ledger, dict) or read_ledger.get("schema") != "suttaflow-source-readings-v1":
            probs.append({"code": "SOURCE_READING_LEDGER_INVALID", "item": "source_readings"})
            readings = []
        else:
            readings = read_ledger.get("records")
    if not isinstance(readings, list):
        probs.append({"code": "SOURCE_READING_LEDGER_INVALID", "item": "source_readings"})
        readings = []
    used_caps: set[str] = set()
    reading_ids = set()
    for record in readings:
        if not isinstance(record, dict) or not _nonempty(record.get("id")):
            probs.append({"code": "SOURCE_READING_INVALID", "item": "source_readings"})
            continue
        if record["id"] in reading_ids:
            probs.append({"code": "SOURCE_READING_DUPLICATE_ID", "item": record["id"]})
        reading_ids.add(record["id"])
        capture_id = record.get("capture_id")
        if not _nonempty(capture_id) or not _reading_valid(record, latest.get(capture_id, {})):
            probs.append({"code": "SOURCE_READING_INVALID", "item": record["id"]})
            continue
        used_caps.add(capture_id)
    entries = decisions.get("decisions", [])
    read_lex = set()
    for decision in entries if isinstance(entries, list) else []:
        if not isinstance(decision, dict) or not isinstance(decision.get("lexicon", []), list):
            continue
        for lexicon in decision.get("lexicon", []):
            if isinstance(lexicon, dict) and lexicon.get("status") == "READ" and _nonempty(lexicon.get("source")) \
                    and isinstance(lexicon.get("locator"), dict) and lexicon["locator"] and _nonempty(lexicon.get("reading")):
                read_lex.add(_lexicon_identity(lexicon["source"]))
    groups = {group["key"] for group in src["groups"] if isinstance(group, dict) and _nonempty(group.get("key"))}
    listed_caps = set()
    listed_lex = set()
    item_ids = set()
    for it in src["items"]:
        if not isinstance(it, dict) or not _nonempty(it.get("id")):
            probs.append({"code": "SOURCE_LIST_ITEM_INVALID", "item": "items"})
            continue
        if it["id"] in item_ids:
            probs.append({"code": "SOURCE_LIST_DUPLICATE_ID", "item": it["id"]})
        item_ids.add(it["id"])
        ev = it.get("evidence", {})
        if not isinstance(ev, dict):
            probs.append({"code": "SOURCE_LISTED_WITHOUT_EVIDENCE", "item": it["id"]})
            continue
        if not _nonempty(it.get("group")) or it["group"] not in groups:
            probs.append({"code": "SOURCE_LIST_UNKNOWN_GROUP", "item": it["id"]})
        if "capture" in ev:
            if not _nonempty(ev["capture"]) or ev["capture"] not in used_caps:
                probs.append({"code": "SOURCE_LISTED_WITHOUT_READING", "item": it["id"]})
            if _nonempty(ev["capture"]):
                listed_caps.add(ev["capture"])
        elif "lexicon_source" in ev:
            identity = _lexicon_identity(ev["lexicon_source"]) if _nonempty(ev["lexicon_source"]) else None
            if identity not in read_lex:
                probs.append({"code": "SOURCE_LISTED_WITHOUT_READING", "item": it["id"]})
            if identity:
                listed_lex.add(identity)
        else:
            probs.append({"code": "SOURCE_LISTED_WITHOUT_EVIDENCE", "item": it["id"]})
        if not it.get("url") and not it.get("url_note"):
            probs.append({"code": "SOURCE_LINK_MISSING", "item": it["id"]})
    for sid in sorted(used_caps):
        if latest[sid].get("role") in REQUIRED_ROLES and sid not in listed_caps:
            probs.append({"code": "SOURCE_USED_NOT_LISTED", "item": sid})
    for s in sorted(read_lex):
        if s not in listed_lex \
                and not s.startswith(("Vinaya", "Papañcasūdanī")):
            probs.append({"code": "DICTIONARY_USED_NOT_LISTED", "item": s})
    return probs


def render(src: dict) -> str:
    out = [f"Źródła — {src['title_pl']}", ""]
    for g in src["groups"]:
        items = [it for it in src["items"] if it["group"] == g["key"]]
        if not items:
            continue
        out.append(g["label_pl"] + ":")
        for it in items:
            out.append(f"• {it['text_pl']}" + (f" — {it['url']}" if it.get("url") else ""))
        out.append("")
    out.append(src["footer_pl"])
    return "\n".join(out) + "\n"


def check_links(src: dict, timeout: int = 30) -> dict:
    res: dict[str, Any] = {"checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "links": {}}
    for it in src["items"]:
        if not it.get("url"):
            continue
        try:
            req = urllib.request.Request(it["url"], headers={"User-Agent": "SuttaFlow-linkcheck/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res["links"][it["url"]] = r.status
        except Exception as e:  # recorded, never hidden
            res["links"][it["url"]] = repr(e)
    return res


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--sutta", default="mn41")
    ap.add_argument("--cap", default="captures/mn41_2026-10-11")
    ap.add_argument("--check-links", action="store_true")
    a = ap.parse_args()
    try:
        src = json.loads((a.root / "data" / f"{a.sutta}_public_sources_v1.json").read_text(encoding="utf-8"))
        log = json.loads((a.root / a.cap / "capture_log.json").read_text(encoding="utf-8"))
        dec = json.loads((a.root / "data" / f"{a.sutta}_decisions_v1.json").read_text(encoding="utf-8"))
        ledger_path = a.root / "data" / f"{a.sutta}_source_readings_v1.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else None
        p = validate(src, log, dec, read_ledger=ledger)
        rendered = render(src) if not p else None
    except (OSError, ValueError, TypeError, KeyError) as exc:
        p = [{"code": "SOURCE_LIST_INPUT_INVALID", "item": type(exc).__name__, "msg": str(exc)}]
    if p:
        print(json.dumps({"status": "HOLD", "problems": p}, ensure_ascii=False))
        raise SystemExit(2)
    out = a.root / "build" / "RC"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.sutta.upper()}_ZRODLA_OPIS_KANALU.txt").write_text(rendered, encoding="utf-8")
    if a.check_links:
        (a.root / "build" / f"{a.sutta}_link_check.json").write_text(
            json.dumps(check_links(src), ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"problems": p}, ensure_ascii=False))
    raise SystemExit(1 if p else 0)
