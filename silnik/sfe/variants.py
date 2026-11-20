"""Token-level variant report between independently captured Pali witnesses."""
from __future__ import annotations

import difflib
import json
from pathlib import Path

from . import witness as w


def witness_tokens(cap: Path) -> dict[str, list[tuple[str, str]]]:
    """Return per witness a list of (compare_key token, location label)."""
    out: dict[str, list[tuple[str, str]]] = {}
    b = w.bjt_segments((cap / "pali_bjt_bd.htm").read_bytes())
    out["BJT"] = [(t, f"BJT §{s['para']}") for s in b["segments"] for t in w.tokens(s["text"])]
    c = w.cst_mn41((cap / "pali_cst_vri.xml").read_bytes())
    out["CST"] = [(t, f"CST p{i}") for i, p in enumerate(c["paragraphs"]) for t in w.tokens(p["text"])]
    m = w.ms_segments((cap / "pali_ms_sc.json").read_bytes())
    out["MS"] = [(t, s["id"]) for s in m if not s["id"].startswith("mn41:0.") for t in w.tokens(s["text"])]
    return out


def diff(a: list[tuple[str, str]], b: list[tuple[str, str]], na: str, nb: str) -> list[dict]:
    sm = difflib.SequenceMatcher(None, [x[0] for x in a], [x[0] for x in b], autojunk=False)
    rows = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        rows.append({"op": op,
                     na: " ".join(x[0] for x in a[i1:i2]), nb: " ".join(x[0] for x in b[j1:j2]),
                     f"{na}_loc": a[i1][1] if i1 < len(a) else a[-1][1],
                     f"{nb}_loc": b[j1][1] if j1 < len(b) else b[-1][1]})
    return rows


def report(cap: Path) -> dict:
    tok = witness_tokens(cap)
    res = {"token_counts": {k: len(v) for k, v in tok.items()},
           "BJT_vs_CST": diff(tok["BJT"], tok["CST"], "BJT", "CST"),
           "BJT_vs_MS": diff(tok["BJT"], tok["MS"], "BJT", "MS"),
           "CST_vs_MS": diff(tok["CST"], tok["MS"], "CST", "MS"),
           "cst_variant_notes": w.cst_mn41((cap / "pali_cst_vri.xml").read_bytes())["notes"],
           "method": "difflib on NFC/casefold tokens; hyphens, apostrophes removed; ṁ→ṃ. "
                     "Orthographic-only differences are still listed; classification is manual."}
    return res


if __name__ == "__main__":
    import sys
    r = report(Path(sys.argv[1]))
    Path(sys.argv[2]).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(r["token_counts"], {k: len(v) for k, v in r.items() if isinstance(v, list)})
