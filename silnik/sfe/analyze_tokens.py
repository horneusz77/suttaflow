"""DPD analysis of every token of the BJT MN 41 segments (no selection, no guessing)."""
from __future__ import annotations
import json, re, sys, unicodedata
from collections import Counter
from pathlib import Path
from . import witness as w
from .dpd import Dpd

def lookup_key(surface: str) -> str:
    s = unicodedata.normalize("NFC", surface).lower().replace("ṁ", "ṃ")
    s = re.sub(r"(?<=\w)-(?=\w)", "", s)
    return s.replace("'", "").replace("’", "")

def run(cap: Path, db: Path, pin: Path, out: Path) -> dict:
    d = Dpd(db, pin)
    segs = w.bjt_segments((cap / "pali_bjt_bd.htm").read_bytes())["segments"]
    rows, cache = [], {}
    for si, s in enumerate(segs):
        for m in w.TOKEN.finditer(s["text"]):
            key = lookup_key(m.group())
            if key not in cache:
                r = d.lookup(key)
                cache[key] = {"status": r["status"], "n_headwords": len(r["headwords"]),
                              "headwords": [{"id": h["id"], "lemma_1": h["lemma_1"], "pos": h["pos"],
                                             "meaning_1": h["meaning_1"]} for h in r["headwords"]],
                              "readings": r["readings"], "deconstructor": r["deconstructor"]}
            rows.append({"seg": si, "para": s["para"], "surface": m.group(), "key": key,
                         "char_in_seg": [m.start(), m.end()], "status": cache[key]["status"]})
    st = Counter(r["status"] for r in rows)
    res = {"dpd_release": d.pin["release"], "db_sha256": d.pin["db_sha256"], "tokens": len(rows),
           "distinct_forms": len(cache), "status_counts": dict(st), "rows": rows, "forms": cache}
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res

if __name__ == "__main__":
    r = run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    print(r["tokens"], r["distinct_forms"], r["status_counts"])
    print("NOT FOUND:", sorted(k for k, v in r["forms"].items() if v["status"] == "NOT_IN_LOOKUP"))
