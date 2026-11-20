"""Full bidirectional Pali↔Polish alignment for MN 41.

Manual groups (§§1–14, 44) come from data/mn41_alignment_manual_v1.json.
The repeated formula §§15–43 is aligned by rule and *verified per instance*: each
paragraph must contain the expected realm/target on both sides, the modal idiom
(ṭhānaṃ … vijjati ↔ 'możliwe jest'), the question (Taṃ kissa hetu? ↔ 'Dlaczego tak
jest?') and the reason clause. Any deviation is reported, never silently accepted.
"""
from __future__ import annotations

import json
from pathlib import Path
import zipfile

from . import witness as w

GROUP_STATUSES = frozenset({"OK", "OK_NOTE", "MINOR", "VARIANT", "OPEN", "CHECK_FAILED"})


def _identifier(value) -> bool:
    return isinstance(value, str) and bool(value) and not any(c.isspace() or c == "\0" for c in value)

# Pali realm key (compare_key form, as in BJT) -> required Polish substring
REALMS = {
    15: ("khattiyamahāsālānaṃ", "khattiyamahāsālā"), 16: ("brāhmaṇamahāsā", "brāhmaṇamahāsālā"),
    17: ("gahapatimahāsālānaṃ", "gahapatimahāsālā"), 18: ("cātummahārājikānaṃ", "Czterech Wielkich Królów"),
    19: ("tāvatiṃsānaṃ", "Trzydziestu Trzech"), 20: ("yāmānaṃ", "Yāmy"), 21: ("tusitānaṃ", "Tusity"),
    22: ("nimmānaratīnaṃ", "Nimmānaratī"), 23: ("paranimmitavasavattīnaṃ", "Paranimmitavasavattī"),
    24: ("brahmakāyikānaṃ", "Brahmakāyikā"), 25: ("ābhānaṃ", "(Ābhā)"), 26: ("parittābhānaṃ", "Parittābhā"),
    27: ("appamāṇābhānaṃ", "Appamāṇābhā"), 28: ("ābhassarānaṃ", "Ābhassarā"), 29: ("subhānaṃ", "(Subhā)"),
    30: ("parittasubhānaṃ", "Parittasubhā"), 31: ("appamāṇasubhānaṃ", "Appamāṇasubhā"),
    32: ("subhakiṇṇakānaṃ", "Subhakiṇṇā"), 33: ("vehapphalānaṃ", "Vehapphalā"), 34: ("avihānaṃ", "Aviha"),
    35: ("atappānaṃ", "Atappa"), 36: ("sudassānaṃ", "Sudassa"), 37: ("sudassīnaṃ", "Sudassī"),
    38: ("akaniṭṭhakānaṃ", "Akaniṭṭha"), 39: ("ākāsānañcāyatanūpagānaṃ", "nieskończonej przestrzeni"),
    40: ("viññāṇañcāyatanūpagānaṃ", "nieskończonej świadomości"), 41: ("ākiñcaññāyatanūpagānaṃ", "nicości"),
    42: ("nevasaññānāsaññāyatanūpagānaṃ", "ani-postrzegania-ani-niepostrzegania"),
    43: ("āsavānaṃ khayā", "zniszczenie skaz"),
}


def formula_groups(pali: list[dict], pl: list[dict]) -> tuple[list[dict], list[dict]]:
    groups: list[dict] = []
    problems: list[dict] = []
    for sec, (pkey, plkey) in REALMS.items():
        ps = [s for s in pali if s["para"] == sec]
        us = [u for u in pl if u["sec"] == sec]
        if not ps or not us:
            problems.append({"sec": sec, "failed": (["missing_pali_units"] if not ps else [])
                             + (["missing_pl_units"] if not us else [])})
            continue
        ptxt = w.compare_key(" ".join(s["text"] for s in ps))
        checks = {
            "pali_target": w.compare_key(pkey) in ptxt.replace(" ", "") or w.compare_key(pkey) in ptxt,
            "pali_modal": "ṭhānaṃ kho panetaṃ vijjati" in ptxt,
            "pali_question": "taṃ kissa hetu" in ptxt,
            "pali_reason": "tathā hi so dhammacārī samacārī" in ptxt,
            "pl_target": bool(us) and plkey in us[0]["text"],
            "pl_modal": any("możliwe jest" in u["text"] for u in us),
            "pl_question": any(u["text"].startswith("Dlaczego tak jest?") for u in us),
            "pl_reason": any(u["text"].startswith("Ponieważ postępuje zgodnie z Dhammą i w sposób prawy") for u in us),
            "pl_target_twice": sum(u["text"].count(plkey) for u in us) >= 2,
        }
        bad = [k for k, v in checks.items() if not v]
        q = [s["id"] for s in ps if "kissa hetu" in w.compare_key(s["text"])]
        r = [s["id"] for s in ps if "tathā hi so" in w.compare_key(s["text"])]
        main = [s["id"] for s in ps if s["id"] not in q + r]
        if len(ps) == 3:   # §17-type: question merged in second clause
            main, q = [ps[0]["id"]], [ps[1]["id"]]
        groups += [{"pali": main, "pl": [us[0]["id"]], "status": "OK" if not bad else "CHECK_FAILED",
                    "rule": "formula-wish+modal", "checks": checks},
                   {"pali": q, "pl": [u["id"] for u in us if u["text"].startswith("Dlaczego")], "status": "OK", "rule": "formula-question"},
                   {"pali": r, "pl": [u["id"] for u in us if u["text"].startswith("Ponieważ")], "status": "OK", "rule": "formula-reason"}]
        if bad:
            problems.append({"sec": sec, "failed": bad})
    return groups, problems


def validate_groups(pali: list[dict], pl: list[dict], groups: list[dict],
                    formula_problems: list[dict] | None = None) -> dict:
    """Validate actual relations independently of their aggregate coverage counts.

    This validator accepts identifiers from any sutta. The MN41 extraction and
    formula adapter below remains separate; no unverified MN53 segmentation is
    inferred here. An explicitly recorded omission/addition still blocks full
    coverage until corrected; merely labelling an exception cannot waive it.
    """
    problems: list[dict] = []
    normalised: list[dict] = []
    group_ids = set()
    for number, group in enumerate(groups):
        where = f"groups[{number}]"
        if not isinstance(group, dict):
            problems.append({"code": "GROUP_INVALID", "where": where})
            continue
        row = dict(group)
        if "id" in row:
            if not _identifier(row["id"]):
                problems.append({"code": "GROUP_ID_INVALID", "where": where})
            elif row["id"] in group_ids:
                problems.append({"code": "GROUP_ID_DUPLICATE", "where": where, "id": row["id"]})
            else:
                group_ids.add(row["id"])
        status = row.get("status")
        if not isinstance(status, str) or status not in GROUP_STATUSES:
            problems.append({"code": "GROUP_STATUS_INVALID", "where": where})
            row["status"] = "INVALID"
        elif status == "CHECK_FAILED":
            problems.append({"code": "GROUP_CHECK_FAILED", "where": where})
        for side in ("pali", "pl"):
            values = row.get(side)
            if not isinstance(values, list) or any(not _identifier(value) for value in values):
                problems.append({"code": "GROUP_UNIT_IDS_INVALID", "where": where, "side": side})
                row[side] = [value for value in values if _identifier(value)] if isinstance(values, list) else []
            if not row[side]:
                problems.append({"code": "GROUP_ONE_SIDED", "where": where, "side": side,
                                 "exception": row.get("exception")})
        normalised.append(row)
    groups = normalised
    source_ids: dict[str, list[str]] = {}
    for side, units in (("pali", pali), ("pl", pl)):
        if not units:
            problems.append({"code": "SOURCE_UNITS_EMPTY", "side": side})
        source_ids[side] = []
        for unit in units:
            if not isinstance(unit, dict) or not _identifier(unit.get("id")):
                problems.append({"code": "SOURCE_UNIT_ID_INVALID", "side": side})
                continue
            source_ids[side].append(unit["id"])
            if not isinstance(unit.get("text"), str) or not unit["text"].strip():
                problems.append({"code": "SOURCE_UNIT_TEXT_EMPTY", "side": side, "id": unit.get("id")})
        duplicate_ids = sorted({value for value in source_ids[side] if source_ids[side].count(value) > 1})
        if duplicate_ids:
            problems.append({"code": "SOURCE_UNIT_ID_DUPLICATE", "side": side, "ids": duplicate_ids})
    pali_ids, pl_ids = source_ids["pali"], source_ids["pl"]
    cov_p = [i for g in groups for i in g["pali"]]
    cov_l = [i for g in groups for i in g["pl"]]
    res = {
        "pali_units": len(pali_ids), "pl_units": len(pl_ids), "groups": len(groups),
        "pali_unmapped": sorted(set(pali_ids) - set(cov_p)), "pl_unmapped": sorted(set(pl_ids) - set(cov_l)),
        "pali_unknown_ids": sorted(set(cov_p) - set(pali_ids)), "pl_unknown_ids": sorted(set(cov_l) - set(pl_ids)),
        "pali_mapped_twice": sorted({i for i in cov_p if cov_p.count(i) > 1}),
        "pl_mapped_twice": sorted({i for i in cov_l if cov_l.count(i) > 1}),
        "formula_problems": formula_problems or [],
        "group_problems": problems,
        "input_problems": [],
        "status_counts": {k: sum(1 for g in groups if g["status"] == k) for k in sorted({g["status"] for g in groups})},
        "groups_detail": groups,
    }
    res["complete"] = not any(res[k] for k in ("pali_unmapped", "pl_unmapped", "pali_unknown_ids",
                                                "pl_unknown_ids", "pali_mapped_twice", "pl_mapped_twice", "formula_problems",
                                                "group_problems", "input_problems"))
    return res


def build(cap: Path, manual: Path) -> dict:
    try:
        bj = w.bjt_segments((cap / "pali_bjt_bd.htm").read_bytes())["segments"]
        seen: dict[int, int] = {}
        for s in bj:
            seen[s["para"]] = seen.get(s["para"], 0) + 1
            s["id"] = f"bjt.§{s['para']}.{seen[s['para']]}"
        pl = w.pl_canonical((cap / "pl_mn41_doc.docx").read_bytes())["units"]
        man = json.loads(manual.read_text(encoding="utf-8"))
        if not isinstance(man, dict) or not isinstance(man.get("groups"), list):
            raise ValueError("alignment groups must be an array")
    except (OSError, ValueError, KeyError, IndexError, StopIteration, TypeError, zipfile.BadZipFile) as exc:
        result = validate_groups([], [], [])
        result["pali_units"] = result["pl_units"] = None
        result["input_problems"] = [{"code": "ALIGNMENT_INPUT_MISSING" if isinstance(exc, FileNotFoundError)
                                    else "ALIGNMENT_INPUT_INVALID", "error_type": type(exc).__name__, "msg": str(exc)}]
        result["complete"] = False
        return result
    fg, problems = formula_groups(bj, pl)
    return validate_groups(bj, pl, man["groups"] + fg, problems)


if __name__ == "__main__":
    import sys
    r = build(Path(sys.argv[1]), Path(sys.argv[2]))
    Path(sys.argv[3]).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in r.items() if k != "groups_detail"})
