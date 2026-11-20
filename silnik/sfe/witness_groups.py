"""DEC-03 (approved by the project owner 2026-10-11): witness groups, Sujato terminology, calques.

1. Witness groups. HH and Sujato count as ONE group in a segment where their texts are
   identical after orthographic normalisation (case, punctuation, contractions), and as
   TWO groups elsewhere. Bodhi and Ṭhānissaro are separate groups. This module only
   counts which independent groups EXIST for a segment; whether they AGREE on a reading
   is a philological judgement recorded in the decision files, not computed here.
2. Terminology. config/terminology_hh_sujato_v1.json lists renderings where Sujato and
   HH systematically differ. Every entry carries evidence segments that are re-verified
   against captured, hashed texts on every run (an entry whose evidence no longer
   matches is an error, not a silent pass). Polish words that mirror Sujato's choice are
   flagged for review — they are not automatically wrong.
3. Calques. A Polish cue word is flagged when its English counterpart occurs in HH or
   Sujato for the same section but in NO DPD gloss of any Pali word of that section.
   Heuristic with a short cue list: it finds known patterns, it cannot prove absence.
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path
from typing import TypedDict

from . import witness as w

class WitnessGroup(TypedDict, total=False):
    status: str
    groups: int
    word_ratio: float


CONTRACTIONS = {
    "it’s": "it is", "that’s": "that is", "there’s": "there is", "what’s": "what is",
    "don’t": "do not", "doesn’t": "does not", "didn’t": "did not", "isn’t": "is not",
    "aren’t": "are not", "wasn’t": "was not", "weren’t": "were not", "can’t": "cannot",
    "won’t": "will not", "wouldn’t": "would not", "shouldn’t": "should not",
    "they’re": "they are", "you’re": "you are", "we’re": "we are", "i’m": "i am",
    "they’ve": "they have", "you’ve": "you have", "we’ve": "we have", "i’ve": "i have",
    "they’ll": "they will", "you’ll": "you will", "i’ll": "i will", "he’s": "he is",
    "she’s": "she is", "let’s": "let us",
}


def normalize_en(t: str) -> list[str]:
    t = t.lower().replace("'", "’")
    for k, v in CONTRACTIONS.items():
        t = re.sub(rf"\b{re.escape(k)}", v, t)
    return re.findall(r"[a-zà-žāīūṁṃṅñṭḍṇḷ]+", t)


def hh_sujato_groups(hh: dict, suj: dict) -> dict:
    """Per Mahāsaṅgīti segment: 1 group if identical after normalisation, else 2."""
    seg: dict[str, WitnessGroup] = {}
    for k in dict.fromkeys(list(suj) + list(hh)):
        s, h = suj.get(k, ""), hh.get(k, "")
        if not s.strip() and not h.strip():
            continue
        if not s.strip():
            seg[k] = {"status": "SUJATO_ABSENT", "groups": 1}
            continue
        if not h.strip() or ("…" in h and "…" not in s):
            # conservative: an abbreviated HH segment is not counted as a full second witness
            seg[k] = {"status": "HH_ABSENT_OR_ABBREVIATED", "groups": 1}
            continue
        a, b = normalize_en(h), normalize_en(s)
        ratio = round(difflib.SequenceMatcher(None, a, b).ratio(), 3)
        seg[k] = {"status": "IDENTICAL" if a == b else "DIFFERENT", "groups": 1 if a == b else 2,
                  "word_ratio": ratio}
    both = [v for v in seg.values() if v["status"] in ("IDENTICAL", "DIFFERENT")]
    return {
        "segments": seg,
        "counts": {s: sum(1 for v in seg.values() if v["status"] == s)
                   for s in ("IDENTICAL", "DIFFERENT", "HH_ABSENT_OR_ABBREVIATED", "SUJATO_ABSENT")},
        # sensitivity: how many DIFFERENT segments would collapse under a looser rule
        "different_but_word_ratio_ge_0_9": sum(1 for v in both if v["status"] == "DIFFERENT" and v["word_ratio"] >= 0.9),
    }


def verify_lexicon(lex: dict, capdirs: list[Path]) -> list[dict]:
    """Re-check every evidence segment of the terminology lexicon against captured texts."""
    texts: dict[str, dict] = {}
    for d in capdirs:
        for f in d.glob("*.json"):
            if f.name.endswith(".headers.json") or f.name == "capture_log.json":
                continue
            try:
                texts[f.stem] = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        if (d / "en_sujato_dep.bin").is_file():
            texts["en_sujato_dep"] = json.loads((d / "en_sujato_dep.bin").read_text(encoding="utf-8"))["translation_text"]
    probs = []
    for e in lex["entries"]:
        for ev in e["evidence"]:
            for role, rx in (("pali", e["pali_rx"]), ("sujato", e["sujato_rx"]), ("hh", e["hh_rx"])):
                src = ev.get(role)
                if src is None:
                    continue
                t = texts.get(src, {}).get(ev["seg"])
                if t is None or not re.search(rx, t, re.I):
                    probs.append({"entry": e["id"], "seg": ev["seg"], "role": role, "source": src})
    return probs


def _sec(u: dict) -> int | None:
    return int(u["sec"]) if str(u["sec"]).isdigit() else None


def ms_section(sec, ms_keys) -> str | None:
    if sec is None:
        return None
    sec = int(sec)
    for k in dict.fromkeys(x.split(":")[1].rsplit(".", 1)[0] for x in ms_keys):
        a, _, b = k.partition("-")
        if a.isdigit() and int(a) <= sec <= int(b or a):
            return k
    return None


def _section_en(src: dict, prefix: str, msk: str) -> str:
    return " ".join(v for k, v in src.items() if k.startswith(f"{prefix}:{msk}."))


def terminology_scan(pl_units: list[dict], pali_by_para: dict, lex: dict) -> list[dict]:
    out = []
    for u in pl_units:
        p = w.compare_key(pali_by_para.get(_sec(u), ""))
        for e in lex["entries"]:
            if not e.get("pl_flag_rx"):
                continue
            m = re.search(e["pl_flag_rx"], u["text"], re.I)
            if m and (not e.get("pali_required") or re.search(e["pali_rx"], p, re.I)):
                out.append({"unit": u["id"], "entry": e["id"], "polish": m.group(0),
                            "sujato": e["sujato_en"], "hh": e["hh_en"]})
    return out


class GlossIndex:
    """English glosses of every DPD headword reachable from the Pali tokens of a section."""

    def __init__(self, dpd):
        self.dpd, self.cache = dpd, {}

    def glosses(self, form: str) -> str:
        if form not in self.cache:
            r = self.dpd.lookup(form)
            parts = [form]
            for dc in r["deconstructor"][:1]:
                parts += [x.strip() for x in dc.split("+")]
            g = []
            for f in [form] + parts[1:]:
                rr = r if f == form else self.dpd.lookup(f)
                for h in rr["headwords"]:
                    g += [h.get("meaning_1") or "", h.get("meaning_lit") or "", h.get("meaning_2") or ""]
            self.cache[form] = " | ".join(g).lower()
        return self.cache[form]

    def section(self, text: str) -> str:
        return " ".join(self.glosses(t) for t in set(w.tokens(text)))


def calque_scan(pl_units: list[dict], pali_by_para: dict, hh: dict, suj: dict, cues: dict,
                gi: GlossIndex, prefix: str = "mn41") -> list[dict]:
    out, gl_cache = [], {}
    for u in pl_units:
        msk = ms_section(_sec(u), suj)
        if msk is None:
            continue
        en = {"HH": _section_en(hh, prefix, msk), "Sujato": _section_en(suj, prefix, msk)}
        for c in cues["cues"]:
            m = re.search(c["pl_rx"], u["text"], re.I)
            if not m:
                continue
            who = [k for k, t in en.items() if re.search(c["en_rx"], t, re.I)]
            if not who:
                continue
            sec = _sec(u)
            if sec not in gl_cache:
                gl_cache[sec] = gi.section(pali_by_para.get(sec, ""))
            if re.search(c.get("gloss_rx", c["en_rx"]), gl_cache[sec], re.I):
                continue
            out.append({"unit": u["id"], "cue": c["id"], "polish": m.group(0), "english_in": who,
                        "pali_basis_in_dpd_glosses": False})
    return out
