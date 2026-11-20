"""Assemble the MN 41 RC document from the captured Polish candidate + recorded revisions.

Revisions are exact (unit_id, old, new) replacements read from data/mn41_rc_revisions_<version>.json
(v1 = RC1, v2 = RC2 — both kept reproducible; v3 = RC2.1);
the build fails if an `old` string is not found exactly once in its unit. Footnotes:
original native footnotes are carried over unless replaced; new ones are attached to units.
Outputs the DOCX plus a JSON 'rc_text' (canonical text per unit) for re-alignment QA.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from . import rcdoc
from . import sources_list
from . import witness as w

LATEST = "v3"


def sources_section(root: Path, rel: str) -> dict:
    """'Źródła' section generated from the validated public source list (one source of truth)."""
    src = json.loads((root / rel).read_text(encoding="utf-8"))
    paras = []
    for g in src["groups"]:
        items = [it for it in src["items"] if it["group"] == g["key"]]
        if items:
            paras.append({"t": "h2", "runs": [g["label_pl"]]})
            paras += [{"t": "li", "runs": [it["text_pl"] + (f" — {it['url']}" if it.get("url") else "")]} for it in items]
    paras.append({"t": "p", "runs": [src["footer_pl"]]})
    return {"heading": "Źródła", "paragraphs": paras}


def build(root: Path, version: str = LATEST) -> tuple[bytes, dict]:
    cap = root / "captures" / "mn41_2026-10-11"
    pl = w.pl_canonical((cap / "pl_mn41_doc.docx").read_bytes())
    rev = json.loads((root / "data" / f"mn41_rc_revisions_{version}.json").read_text(encoding="utf-8"))
    units = {u["id"]: dict(u) for u in pl["units"]}
    applied = []
    for r in rev["text_revisions"]:
        for uid in r["units"]:
            t = units[uid]["text"]
            if t.count(r["old"]) != 1:
                raise SystemExit(f"REVISION_ANCHOR_NOT_UNIQUE {r['id']} {uid} count={t.count(r['old'])}")
            units[uid]["text"] = t.replace(r["old"], r["new"], 1)
            applied.append({"id": r["id"], "unit": uid})
    fn_text = dict(pl["footnotes"])
    for k, v in rev["footnote_replacements"].items():
        fn_text[k] = v
    new_fn = rev["new_footnotes"]  # {unit_id: [{"after": "exact text", "text": "..."}]}

    blocks: list[dict[str, Any]] = [{"t": "title", "runs": ["Ludzie z Sālā"]},
              {"t": "subtitle", "runs": ["Sāleyyakasutta · Majjhima Nikāya 41"]}]
    for label, val in rev["metadata"]:
        blocks.append({"t": "meta", "runs": [{"b": label + ": "}, val]})
    blocks.append({"t": "h1", "runs": ["Przekład"]})

    order = [u["id"] for u in pl["units"]]
    current_sec = None
    para: dict[str, Any] | None = None
    for uid in order:
        u = units[uid]
        sec = u["sec"]
        if sec != current_sec or u.get("para_start"):
            if para:
                blocks.append(para)
            label = [f"[§{sec}] "] if sec != current_sec and sec != "colophon" else []
            para = {"t": "p", "runs": list(label)}
            current_sec = sec
        else:
            if para is None:
                raise ValueError("POLISH_PARAGRAPH_ABSENT")
            para["runs"].append(" ")
        text = u["text"]
        inserts = sorted(new_fn.get(uid, []), key=lambda x: text.index(x["after"]) + len(x["after"]))
        pos = 0
        pieces = []
        for ins in inserts:
            cut = text.index(ins["after"]) + len(ins["after"])
            pieces.append(("t", text[pos:cut])); pieces.append(("fn", ins["text"])); pos = cut
        pieces.append(("t", text[pos:]))
        for kind, val in pieces:
            if kind == "fn":
                para["runs"].append({"fn": val}); continue
            for part in re.split(r"(⟨fn\d+⟩)", val):
                m = re.fullmatch(r"⟨fn(\d+)⟩", part)
                if m:
                    para["runs"].append({"fn": fn_text[m.group(1)]})
                elif part:
                    para["runs"].append(part)
    if para is None:
        raise ValueError("POLISH_PARAGRAPH_ABSENT")
    blocks.append(para)
    for sec in rev["after_translation"]:
        if "generated_from" in sec:
            sec = sources_section(root, sec["generated_from"])
        blocks.append({"t": "h1", "runs": [sec["heading"]]})
        for p in sec["paragraphs"]:
            blocks.append({"t": p.get("t", "p"), "runs": p["runs"]})
    rc_text = {uid: re.sub(r"⟨fn\d+⟩", "", units[uid]["text"]) for uid in order}
    return rcdoc.build(blocks), {"applied": applied, "rc_text": rc_text, "rc_units_raw": {uid: units[uid]["text"] for uid in order},
                                 "footnotes_total": sum(1 for b in blocks for r in b["runs"] if isinstance(r, dict) and "fn" in r)}


def lector_text(root: Path, version: str = LATEST, name: str = "RC2", approved: str | None = None) -> str:
    """Plain text for recording: sutta text without § labels or footnotes, then the separated commentary."""
    cap = root / "captures" / "mn41_2026-10-11"
    units = w.pl_canonical((cap / "pl_mn41_doc.docx").read_bytes())["units"]
    _, info = build(root, version)
    rev = json.loads((root / "data" / f"mn41_rc_revisions_{version}.json").read_text(encoding="utf-8"))
    paras: list[str] = []
    cur: list[str] = []
    sec = None
    for u in units:
        if (u["sec"] != sec or u.get("para_start")) and cur:
            paras.append(" ".join(cur)); cur = []
        sec = u["sec"]
        cur.append(info["rc_text"][u["id"]])
    paras.append(" ".join(cur))
    com = rev["after_translation"][0]["paragraphs"][:2]
    head = (f"MN 41 · Ludzie z Sālā — TEKST DO NAGRANIA ({name})\n"
            + (f"STATUS: ZATWIERDZONE do nagrania przez właściciela projektu ({approved}). " if approved else
               "STATUS: WSTRZYMANE — NIE NAGRYWAĆ do decyzji GO właściciela projektu. ")
            + "Tekst nie został sprawdzony przez specjalistę znającego pali (DEC-01).\n"
            "Komentarz dla lektora nie jest częścią kanonicznej sutty i jest wyraźnie oddzielony.\n\n")
    tail = ("\n\n— KONIEC TEKSTU SUTTY —\n\nKOMENTARZ DLA LEKTORA (opracowanie redakcyjne, nie słowa sutty):\n\n"
            + "\n\n".join(p["runs"][0] for p in com) + "\n")
    return head + "\n\n".join(paras) + tail


if __name__ == "__main__":
    root = Path(sys.argv[1])
    version = sys.argv[2] if len(sys.argv) > 2 else LATEST
    name = {"v1": "RC1", "v2": "RC2", "v3": "RC2.1"}[version]
    docx, info = build(root, version)
    out = root / "build" / "RC"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"MN41_{name}.docx").write_bytes(docx)
    (out / f"MN41_{name}_text.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    if version != "v1":
        (out / f"MN41_{name}_TEKST_DLA_LEKTORA_WSTRZYMANE.txt").write_text(lector_text(root, version, name), encoding="utf-8")
    print(len(docx), len(info["applied"]), info["footnotes_total"])
