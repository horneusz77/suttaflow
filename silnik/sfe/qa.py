"""SuttaFlow Evidence QA (RC) — the single production gate.

evaluate() is the ONLY gate implementation; the CLI, the tests and the dashboard export
all call it. It never outputs PASS and never authorises publication.

Statuses (independent, all reported):
  SOURCE_AUTHENTICATED       per source: bytes match an anchor outside our control
                             (GitHub git blob at pinned commit; GitHub release digest)
  SOURCE_CORROBORATED        no external anchor, but an independent copy (Internet Archive)
                             agrees lexically
  SOURCE_SELF_CAPTURE        only our own capture; usable as a witness, flagged
  FULL_COVERAGE_REVIEW_READY denominator derived from raw Pali bytes; every Pali and Polish
                             unit mapped exactly once; every non-OK unit has a decision record
  TECHNICAL_EVIDENCE_READY   all technical checks pass and the release manifest matches the
                             externally published trust anchor
  HUMAN_PALIST_REVIEW        ABSENT unless a human attestation is supplied (identity is NOT
                             verified by this code; it can only refuse missing attestations)
Publication: always False here — an editorial decision outside this code.
"""
from __future__ import annotations

import datetime as dt
import difflib
import os
import hashlib
import json
import re
import statistics
import zipfile
from pathlib import Path
from urllib.parse import urlparse

from . import align as A
from . import witness as W
from . import witness_groups as G
from . import source_provenance as SP
from . import sources_list as SL
from . import status_axes as SA
from . import issue_resolution as IR

OFFICIAL_HOSTS = {  # role -> hosts accepted as the carrier for that role
    "HH_EN": {"suttas.hillsidehermitage.org"}, "HH_CATALOGUE": {"suttas.hillsidehermitage.org"},
    "HH_PALI_ROOT": {"suttas.hillsidehermitage.org"}, "HH_COMMENT": {"suttas.hillsidehermitage.org"},
    "THANISSARO_EN": {"www.dhammatalks.org", "dhammatalks.org"},
    "BODHI_EN": {"obo.genaud.net"},            # mirror: accepted only as MIRROR, see flags
    "PALI_BASE": {"buddhadust.net"},
    "PALI_WITNESS": {"raw.githubusercontent.com"}, "COMMENTARY": {"raw.githubusercontent.com"},
    "CANONICAL_GLOSS": {"raw.githubusercontent.com"},
    "DEPENDENCY_PROBE_ONLY": {"suttacentral.net"}, "POLISH_CANDIDATE": set(),
    "SUJATO_EN": {"raw.githubusercontent.com"},   # DEC-03: additional verifier, never a wording source
}
MIRROR_ROLES = {"BODHI_EN"}
NOW = dt.datetime.now(dt.timezone.utc)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def git_blob(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def manifest_files(root: Path) -> dict[str, str]:
    out = {}
    for sub in ("captures", "data", "config", "sfe", "tests", "legacy", "schemas", "docs"):
        for p in sorted((root / sub).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                out[p.relative_to(root).as_posix()] = sha256_file(p)
    return out


def build_manifest(root: Path) -> dict:
    m = {"schema": "suttaflow-release-manifest-v1", "files": manifest_files(root)}
    m["manifest_core_sha256"] = hashlib.sha256(json.dumps(m["files"], sort_keys=True).encode()).hexdigest()
    return m


def check_sources(capdir: Path, latest: dict, err, warn) -> dict:
    src_status = {}
    for sid, r in latest.items():
        f = capdir / r.get("file", "")
        if r.get("status") != "CAPTURED" or not f.is_file():
            err("SOURCE_NOT_CAPTURED", sid); continue
        if sha256_file(f) != r["sha256"]:
            err("SOURCE_HASH_MISMATCH", sid)
        t = dt.datetime.fromisoformat(r["fetched_at_utc"])
        if t > NOW + dt.timedelta(minutes=5):
            err("DATE_IN_FUTURE", sid)
        host = urlparse(r.get("url", "")).netloc
        allowed = OFFICIAL_HOSTS.get(r["role"])
        if allowed is None:
            err("UNKNOWN_ROLE", sid, r["role"])
        elif allowed and host not in allowed:
            err("UNAUTHORIZED_WITNESS", sid, f"{host} is not an accepted carrier for {r['role']}")
        anc = r.get("anchor", {})
        if anc.get("type") == "GITHUB_GIT_BLOB":
            ok = git_blob(f.read_bytes()) == anc.get("git_blob_sha1")
            src_status[sid] = "SOURCE_AUTHENTICATED" if ok else "SOURCE_ANCHOR_MISMATCH"
            if not ok:
                err("SOURCE_ANCHOR_MISMATCH", sid, "bytes do not hash to the git blob recorded from GitHub")
        else:
            src_status[sid] = "SOURCE_SELF_CAPTURE"
        if src_status[sid] == "SOURCE_SELF_CAPTURE":
            twins = [o for o, rr in latest.items() if o != sid and rr.get("sha256") == r["sha256"]
                     and rr.get("anchor", {}).get("type") == "GITHUB_GIT_BLOB"]
            if twins:
                src_status[sid] = "SOURCE_CORROBORATED"  # byte-identical to a GitHub-anchored file
        if r["role"] in MIRROR_ROLES:
            warn("MIRROR_CARRIER", sid, "translation read from a mirror; licence/edition not confirmed with publisher")
    return src_status


def _input_problems(root: Path, cap: str) -> list[dict]:
    """Check the external input boundary before any parser or array indexing."""
    problems = []

    def problem(code, path, msg=""):
        problems.append({"code": code, "where": str(path), "msg": msg})

    def load(path, expected_type, missing_code="INPUT_MISSING", optional=False):
        if not path.is_file():
            if not optional:
                problem(missing_code, path.relative_to(root))
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problem("INPUT_JSON_INVALID", path.relative_to(root), type(exc).__name__)
            return None
        if not isinstance(value, expected_type):
            problem("INPUT_SCHEMA_INVALID", path.relative_to(root), f"expected {expected_type.__name__}")
            return None
        return value

    def input_path(base, relative, code, locator):
        if not isinstance(relative, str) or not relative.strip() or "\0" in relative or Path(relative).is_absolute():
            problem(code, locator, "expected a nonempty relative path without NUL")
            return None
        path = base / relative
        try:
            contained = base.resolve() in path.resolve().parents
        except (OSError, ValueError, RuntimeError) as exc:
            problem(code, locator, str(exc))
            return None
        if not contained:
            problem(code, locator, "path must stay within its input directory")
            return None
        return path

    capdir = input_path(root, cap, "INPUT_PATH_INVALID", cap)
    if capdir is None:
        return problems
    for filename, code in (("pali_bjt_bd.htm", "PALI_SOURCE_MISSING"), ("pl_mn41_doc.docx", "POLISH_SOURCE_MISSING")):
        if not (capdir / filename).is_file():
            problem(code, (capdir / filename).relative_to(root))
    json_inputs = {
        root / "data/mn41_alignment_manual_v1.json": dict,
        root / "data/mn41_decisions_v1.json": dict,
        root / "data/mn41_dec03_findings_v1.json": dict,
        root / "config/terminology_hh_sujato_v1.json": dict,
        root / "config/calque_cues_v1.json": dict,
        capdir / "hh_index.json": dict,
        capdir / "hh_mn41_tr.json": dict,
        capdir / "en_sujato_dep.bin": dict,
    }
    parsed = {path: load(path, kind) for path, kind in json_inputs.items()}
    decisions_path = root / "data/mn41_decisions_v1.json"
    decisions = parsed.get(decisions_path)
    if decisions is not None:
        for key in ("decisions", "minor_revisions_proposed"):
            records = decisions.get(key, [])
            if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
                problem("DECISION_SCHEMA_INVALID", decisions_path.relative_to(root), key)
                continue
            for index, record in enumerate(records):
                lexicons = record.get("lexicon", [])
                if not isinstance(lexicons, list) or any(not isinstance(lexicon, dict)
                        or not isinstance(lexicon.get("locator", {}), dict) for lexicon in lexicons):
                    problem("DECISION_SCHEMA_INVALID", decisions_path.relative_to(root), f"{key}[{index}].lexicon")
    for rel in ("data/release_evidence_v2.json", "data/mn41_source_readings_v1.json", "data/owner_decisions_v1.json",
                "data/mn41_status_axes_v1.json", "data/mn41_public_sources_v1.json", "anchors/release_manifest.json"):
        value = load(root / rel, dict, optional=True)
        if rel == "anchors/release_manifest.json" and value is not None and not isinstance(value.get("files"), dict):
            problem("MANIFEST_SCHEMA_INVALID", rel)
    lexicon = parsed.get(root / "config/terminology_hh_sujato_v1.json") or {}
    captures = lexicon.get("captures", [])
    if not isinstance(captures, list) or any(not isinstance(item, str) for item in captures):
        problem("INPUT_SCHEMA_INVALID", "config/terminology_hh_sujato_v1.json", "captures must be paths")
        captures = []
    for relative in dict.fromkeys([cap, *captures]):
        directory = input_path(root, relative, "INPUT_PATH_INVALID", relative)
        if directory is None:
            continue
        log = load(directory / "capture_log.json", list, missing_code="CAPTURE_LOG_MISSING")
        if log is None:
            continue
        ids = set()
        for index, record in enumerate(log):
            locator = f"{relative}/capture_log.json[{index}]"
            if not isinstance(record, dict) or not A._identifier(record.get("id")):
                problem("SOURCE_RECORD_INVALID", locator, "source id is required")
                continue
            if record["id"] in ids:
                problem("SOURCE_DUPLICATE_ID", locator, record["id"])
            ids.add(record["id"])
            anchor = record.get("anchor", {})
            if not isinstance(anchor, dict) or ("type" in anchor and not isinstance(anchor["type"], str)):
                problem("SOURCE_ANCHOR_INVALID", locator, "anchor must be an object with a string type")
            if record.get("status") != "CAPTURED":
                continue
            if not isinstance(record.get("role"), str) or not record["role"].strip() \
                    or ("url" in record and not isinstance(record["url"], str)):
                problem("SOURCE_RECORD_INVALID", locator, "role and supplied URL must be strings")
            path = input_path(directory, record.get("file"), "SOURCE_PATH_INVALID", locator)
            if path is None:
                continue
            if not path.is_file():
                problem("SOURCE_FILE_MISSING", locator, record["id"])
            if not isinstance(record.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
                problem("SOURCE_RECORD_INVALID", locator, "invalid SHA-256")
            try:
                timestamp = dt.datetime.fromisoformat(record["fetched_at_utc"])
                if timestamp.tzinfo is None:
                    raise ValueError("timezone missing")
            except (KeyError, TypeError, ValueError):
                problem("SOURCE_DATE_INVALID", locator)
    return problems


def _blocked_input_report(root: Path | None, problems: list[dict]) -> dict:
    axes = None
    try:
        raw = json.loads((root / "data/mn41_status_axes_v1.json").read_text(encoding="utf-8")) if root is not None else None
        if isinstance(raw, dict):
            axes = {key: raw.get(key, {}).get("value") if isinstance(raw.get(key), dict) else None for key in "ABCDE"}
    except (OSError, ValueError):
        pass  # No axis is inferred when its record cannot be read.
    return {"schema": "suttaflow-qa-rc-v1", "sutta": "mn41", "verdict": "HOLD", "execution_status": "BLOCKED",
            "blocking_stage": "INPUT_VALIDATION", "source_status": {}, "dpd_resource": {"status": "NOT_RUN"},
            "units": {"pali": None, "polish": None, "tokens_offset_checked": None, "group_status_counts": {}},
            "hh_sujato_median_similarity": None, "dec03": None, "status_axes": axes,
            "FULL_COVERAGE_REVIEW_READY": False, "TECHNICAL_EVIDENCE_READY": False,
            "HUMAN_PALIST_REVIEW": "ABSENT", "ready_for_publication": False, "errors": problems, "warnings": []}


def evaluate(root: Path, cap: str = "captures/mn41_2026-10-11", expected_anchor: str | None = None,
             attestations: Path | None = None) -> dict:
    try:
        root = Path(root)
        if "\0" in str(root):
            raise ValueError("NUL in root path")
    except (TypeError, ValueError) as exc:
        return _blocked_input_report(None, [{"code": "INPUT_PATH_INVALID", "where": "root", "msg": str(exc)}])
    try:
        problems = _input_problems(root, cap)
        if problems:
            return _blocked_input_report(root, problems)
        return _evaluate(root, cap, expected_anchor, attestations)
    except (OSError, ValueError, TypeError, KeyError, IndexError, StopIteration, zipfile.BadZipFile) as exc:
        # Known file/container/parser failures are data failures, never a green
        # result. AssertionError and unexpected programming errors are not hidden.
        return _blocked_input_report(root, [{"code": "INPUT_INVALID", "where": "evidence processing",
                                             "msg": f"{type(exc).__name__}: {exc}"}])


def _evaluate(root: Path, cap: str, expected_anchor: str | None, attestations: Path | None) -> dict:
    E: list[dict] = []
    Wn: list[dict] = []
    err = lambda code, where="", msg="": E.append({"code": code, "where": where, "msg": msg})
    warn = lambda code, where="", msg="": Wn.append({"code": code, "where": where, "msg": msg})
    capdir = root / cap

    # 1. Release manifest vs files, and vs the externally published anchor
    mpath = root / "anchors" / "release_manifest.json"
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.is_file() else None
    current = manifest_files(root)
    if manifest is None:
        err("MANIFEST_MISSING", "anchors/release_manifest.json")
    else:
        core = hashlib.sha256(json.dumps(manifest["files"], sort_keys=True).encode()).hexdigest()
        if core != manifest.get("manifest_core_sha256"):
            err("MANIFEST_SELF_HASH", "anchors/release_manifest.json")
        for rel, h in manifest["files"].items():
            if current.get(rel) != h:
                err("FILE_HASH_MISMATCH_OR_MISSING", rel)
        for rel in set(current) - set(manifest["files"]):
            err("UNLISTED_FILE", rel)
        if expected_anchor is None:
            err("TRUST_ANCHOR_NOT_SUPPLIED", "manifest_core_sha256",
                "Supply the hash published outside the package (Drive report) with --expect-anchor")
        elif core != expected_anchor:
            err("TRUST_ANCHOR_MISMATCH", "manifest_core_sha256", f"package {core} != published {expected_anchor}")

    # 2. Sources: anchors, carriers, dates
    log = json.loads((capdir / "capture_log.json").read_text(encoding="utf-8"))
    latest = {}
    for r in log:
        latest[r["id"]] = r
    src_status = check_sources(capdir, latest, err, warn)

    # BJT corroboration with the independent Internet Archive copy (lexical identity)
    wb = capdir / "pali_bjt_bd.wayback_20250324.htm"
    if (capdir / "pali_bjt_bd.htm").is_file() and wb.is_file():
        a = [s["text"] for s in W.bjt_segments((capdir / "pali_bjt_bd.htm").read_bytes())["segments"]]
        b = [s["text"] for s in W.bjt_segments(wb.read_bytes())["segments"]]
        if [W.compare_key(x) for x in a] == [W.compare_key(x) for x in b]:
            src_status["pali_bjt_bd"] = "SOURCE_CORROBORATED"
        else:
            err("BJT_NOT_CORROBORATED", "pali_bjt_bd", "differs lexically from Internet Archive copy 2025-03-24")

    # 3. Denominator from raw bytes; reversible offsets for EVERY segment and EVERY token
    raw = (capdir / "pali_bjt_bd.htm").read_bytes()
    seg = W.bjt_segments(raw)
    ch = seg["_chars"]
    n_tokens = 0
    for i, s in enumerate(seg["segments"]):
        span = raw[s["byte_start"]:s["byte_end"]].decode("utf-8")
        if re.sub(r"<[^>]+>", "", span).replace("&quot;", '"') != s["text"]:
            err("SEGMENT_OFFSET", f"bjt seg {i}")
        for m in W.TOKEN.finditer(s["text"]):
            n_tokens += 1
            g0, g1 = s["char_start"] + m.start(), s["char_start"] + m.end()
            if ch.text[g0:g1] != m.group() or raw[ch.starts[g0]:ch.ends[g1 - 1]].decode("utf-8") != m.group():
                err("TOKEN_OFFSET", f"bjt seg {i} token {m.group()}")
    # byte accounting: body = segments + separators + whitespace, nothing else
    s0, s1 = seg["body_char_range"]
    mask = [False] * (s1 - s0)
    for x in seg["segments"]:
        for k in range(x["char_start"], x["char_end"]):
            mask[k - s0] = True
    covered_sep = 0
    for x in seg["separators"]:
        covered_sep += len(x["text"])
    leftover = "".join(c for k, c in enumerate(ch.text[s0:s1]) if not mask[k])
    leftover = re.sub(r"\|\||\[\s*\d+\s*\]|\s|\d{1,2}\.", "", leftover)
    if leftover:
        err("UNACCOUNTED_SOURCE_TEXT", "pali_bjt_bd", leftover[:120])

    # 4. Alignment (both directions) — recomputed, not read from a stored result
    al = A.build(capdir, root / "data" / "mn41_alignment_manual_v1.json")
    for alignment_key in ("pali_unmapped", "pl_unmapped", "pali_unknown_ids", "pl_unknown_ids",
              "pali_mapped_twice", "pl_mapped_twice", "formula_problems", "group_problems", "input_problems"):
        if al[alignment_key]:
            err("ALIGNMENT_" + alignment_key.upper(), "", json.dumps(al[alignment_key], ensure_ascii=False)[:300])

    # 5. Decisions and lexical locators; current pinned DPD bytes are required.
    dec = json.loads((root / "data" / "mn41_decisions_v1.json").read_text(encoding="utf-8"))
    for problem in IR.validate(root, capdir, al["groups_detail"], dec):
        err(problem["code"], problem["item"], problem["msg"])
    dpd_db = Path(os.environ.get("SUTTAFLOW_DPD_DB", root.parent / "resources" / "dpd" / "dpd.db"))
    from .dpd import Dpd, DpdError
    d = None
    dpd_resource: dict = {"status": "BLOCKED", "sha256": None, "bytes": None, "release": None}
    try:
        d = Dpd(dpd_db, root / "config" / "dpd_pin.json", verify_hash=True)
        dpd_resource = {"status": "VERIFIED", "sha256": d.verified_sha256, "bytes": d.verified_bytes,
                        "release": d.version["dpd_release_version"],
                        "pin_sha256": sha256_file(root / "config" / "dpd_pin.json"),
                        "verification": "SHA256_STREAM_PER_EVALUATION"}
    except DpdError as exc:
        dpd_resource["failure_code"] = "DPD_" + str(exc)
        err(dpd_resource["failure_code"], "dpd", "lexical locators and calque scan NOT_RUN")
    if d is not None:
        for rec in dec["decisions"]:
            for lx in rec.get("lexicon", []):
                loc = lx.get("locator", {})
                if "headword_id" in loc:
                    try:
                        hw = d.headword(int(loc["headword_id"]))
                        if hw["lemma_1"] != loc["lemma_1"]:
                            err("LOCATOR_MISMATCH", rec["id"], f"{loc} -> {hw['lemma_1']}")
                    except Exception as e:
                        err("LOCATOR_MISMATCH", rec["id"], repr(e))

    # 6. Witness availability: HH listed in the OFFICIAL captured index must be read
    idx = json.loads((capdir / "hh_index.json").read_text(encoding="utf-8"))["available_suttas"]
    if "mn41" in idx and latest.get("hh_mn41_tr", {}).get("status") != "CAPTURED":
        err("HH_FALSE_ABSENCE", "hh_mn41_tr")
    hh = json.loads((capdir / "hh_mn41_tr.json").read_text(encoding="utf-8"))
    partial = sorted(k for k, v in hh.items() if "…" in v)
    if partial:
        warn("HH_PARTIAL_COVERAGE", f"{len(partial)} segments abbreviated by HH",
             "fallback to Ñāṇamoli/Bodhi then Ṭhānissaro required for these segments")
    suj = json.loads((capdir / "en_sujato_dep.bin").read_text(encoding="utf-8"))["translation_text"]
    sims = [difflib.SequenceMatcher(None, hh[k], suj[k]).ratio() for k in hh if k in suj and len(suj[k]) > 40]
    dep = round(statistics.median(sims), 3) if sims else None

    # 6b. DEC-03: witness groups per segment, Sujato terminology, calques
    wg = G.hh_sujato_groups(hh, suj)
    source_provenance = SP.from_captures(
        root, capdir, hh, suj, latest,
        evidence_manifest=root / "data" / "mn41_source_provenance_v1.json")
    if wg["counts"]["IDENTICAL"]:
        warn("HH_SUJATO_SHARED_SEGMENTS", f"{wg['counts']['IDENTICAL']} segments",
             "HH = Sujato after normalisation: agreement there counts as ONE witness group (DEC-03)")
    lex = json.loads((root / "config" / "terminology_hh_sujato_v1.json").read_text(encoding="utf-8"))
    term_src = {}
    for c in lex["captures"]:
        cd = root / c
        if cd.resolve() != capdir.resolve():
            lg = json.loads((cd / "capture_log.json").read_text(encoding="utf-8"))
            term_src.update(check_sources(cd, {r["id"]: r for r in lg}, err, warn))
    for pr in G.verify_lexicon(lex, [root / c for c in lex["captures"]]):
        err("TERMINOLOGY_EVIDENCE_MISMATCH", f"{pr['entry']} {pr['seg']}", f"{pr['role']} in {pr['source']}")
    pbp: dict[int, str] = {}
    for s_ in seg["segments"]:
        pbp[s_["para"]] = pbp.get(s_["para"], "") + " " + s_["text"]
    pl_units = W.pl_canonical((capdir / "pl_mn41_doc.docx").read_bytes())["units"]
    fnd = json.loads((root / "data" / "mn41_dec03_findings_v1.json").read_text(encoding="utf-8"))
    term = G.terminology_scan(pl_units, pbp, lex)
    covered_entries = {t["entry"]: t for t in fnd["terminology"] if t.get("scope") == "ALL_FLAGGED_UNITS"}
    for t in term:
        if t["entry"] not in covered_entries:
            err("TERMINOLOGY_FLAG_UNRECORDED", t["unit"], f"{t['entry']}: '{t['polish']}' (Sujato: {t['sujato']}; HH: {t['hh']})")
    for e_, rec in covered_entries.items():
        n = sum(1 for t in term if t["entry"] == e_)
        if n and rec["status"] != "DECIDED":
            warn("TERMINOLOGY_QUESTION_OPEN", rec["id"], f"{e_}: {n} units")
    calq = None
    if d is not None:
        calq = G.calque_scan(pl_units, pbp, hh, suj, json.loads((root / "config" / "calque_cues_v1.json").read_text(encoding="utf-8")),
                             G.GlossIndex(d))
        recorded = {(c["cue"], u) for c in fnd["calques"] for u in c["units"]}
        for c in calq:
            if (c["cue"], c["unit"]) not in recorded:
                err("CALQUE_UNRECORDED", c["unit"], f"{c['cue']}: '{c['polish']}' in {c['english_in']}, no DPD gloss in section")
        d.con.close()

    # 6c. Public source list for channel descriptions: only sources actually read, none omitted
    psrc = root / "data" / "mn41_public_sources_v1.json"
    if psrc.is_file():
        readings_path = root / "data" / "mn41_source_readings_v1.json"
        readings = json.loads(readings_path.read_text(encoding="utf-8")) if readings_path.is_file() else None
        for pr in SL.validate(json.loads(psrc.read_text(encoding="utf-8")), log, dec, read_ledger=readings):
            err(pr["code"], pr["item"])
    else:
        err("SOURCE_LIST_MISSING", "data/mn41_public_sources_v1.json")

    # 7. Reviews and attestations
    human = "ABSENT"
    od = root / "data" / "owner_decisions_v1.json"
    if attestations and attestations.is_file():
        at = json.loads(attestations.read_text(encoding="utf-8"))
        for a in at.get("attestations", []):
            if a.get("type") == "HUMAN_PALIST":
                if not all(a.get(k) for k in ("name", "date", "scope", "statement")):
                    err("REVIEW_ATTESTATION_INCOMPLETE", a.get("name", "?"))
                elif dt.date.fromisoformat(a["date"]) > NOW.date():
                    err("DATE_IN_FUTURE", "attestation")
                else:
                    human = "PRESENT_IDENTITY_UNVERIFIED"
            elif a.get("type") in ("AI_SAME", "AI_OTHER") and a.get("claims_human"):
                err("AI_CLAIMS_HUMAN_REVIEW", a.get("name", "?"))

    cov_ready = bool(al["complete"]) and not any(e["code"].startswith(("ALIGNMENT_", "DECISION_", "UNACCOUNTED", "SEGMENT_", "TOKEN_")) for e in E)
    # 8. Standard 1.5, section 25: recorded status axes must have their basis
    axp = root / "data" / "mn41_status_axes_v1.json"
    axes = json.loads(axp.read_text(encoding="utf-8")) if axp.is_file() else {}
    if not axes:
        err("STATUS_AXES_MISSING", "data/mn41_status_axes_v1.json")
    else:
        owner = json.loads(od.read_text(encoding="utf-8")) if od.is_file() else {}
        evidence_path = root / "data" / "release_evidence_v2.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.is_file() else None
        for pr in SA.validate(axes, owner, cov_ready, human, root=root, evidence=evidence):
            err(pr["code"], "axis " + pr["axis"], pr["msg"])
    tech_ready = not E
    status_axes = {k: axes.get(k, {}).get("value") for k in "ABCDE"} if axes else None
    return {
        "schema": "suttaflow-qa-rc-v1", "sutta": "mn41",
        "source_status": src_status,
        "dpd_resource": dpd_resource,
        "units": {"pali": al["pali_units"], "polish": al["pl_units"], "tokens_offset_checked": n_tokens,
                  "group_status_counts": al["status_counts"]},
        "hh_sujato_median_similarity": dep,
        "source_provenance": source_provenance,
        "dec03": {"witness_groups": wg["counts"], "different_but_word_ratio_ge_0_9": wg["different_but_word_ratio_ge_0_9"],
                  "terminology_flags": {k: sum(1 for t in term if t["entry"] == k) for k in sorted({t["entry"] for t in term})},
                  "calque_suspects": [(c["unit"], c["cue"]) for c in calq] if calq is not None else None,
                  "calque_scan_status": "EXECUTED" if calq is not None else "NOT_RUN",
                  "terminology_sources": term_src},
        "status_axes": status_axes,
        "FULL_COVERAGE_REVIEW_READY": cov_ready,
        "TECHNICAL_EVIDENCE_READY": tech_ready,
        "HUMAN_PALIST_REVIEW": human,
        "ready_for_publication": False,
        "verdict": "TECHNICAL_EVIDENCE_READY" if tech_ready else "HOLD",
        "errors": E, "warnings": Wn,
    }
