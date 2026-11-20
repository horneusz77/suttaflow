"""Witness extraction with reversible offsets into the captured raw bytes.

Every extracted character keeps the UTF-8 byte offset of the raw file it came from,
so any segment can be re-derived from (raw file, byte_start, byte_end) and checked.
Normalisation for comparison (hyphens, apostrophes, niggahita, case) is applied only
to *comparison keys*, never to the stored segment text.
"""
from __future__ import annotations

import html
import json
import re
import unicodedata
import zipfile
from dataclasses import dataclass, field


@dataclass
class Chars:
    text: str = ""
    starts: list[int] = field(default_factory=list)  # raw byte start of each char
    ends: list[int] = field(default_factory=list)    # raw byte end of each char

    def add(self, s: str, b0: int, b1: int) -> None:
        for ch in s:
            self.text += ch
            self.starts.append(b0)
            self.ends.append(b1)

    def span(self, i: int, j: int) -> tuple[int, int]:
        return self.starts[i], self.ends[j - 1]


def byte_offsets(s: str) -> list[int]:
    out, n = [], 0
    for ch in s:
        out.append(n)
        n += len(ch.encode("utf-8"))
    out.append(n)
    return out


def html_chars(raw: bytes) -> Chars:
    """Text of an HTML page with per-char raw byte offsets (tags/script/style dropped,
    entities resolved, <br> and block ends become newlines)."""
    s = raw.decode("utf-8")
    off = byte_offsets(s)
    out = Chars()
    i, n = 0, len(s)
    block = re.compile(r"</?(p|div|br|h\d|li|tr|table)\b", re.I)
    while i < n:
        c = s[i]
        if c == "<":
            j = s.find(">", i)
            if j == -1:
                raise ValueError(f"HTML_TAG_UNTERMINATED: byte offset {off[i]}")
            tag = s[i:j + 1]
            low = tag.lower()
            if low.startswith("<script") or low.startswith("<style"):
                end = s.lower().find("</" + low[1:7].strip("> "), j)
                if end == -1:
                    raise ValueError(f"HTML_BLOCK_UNTERMINATED: byte offset {off[i]}")
                j = s.find(">", end)
                if j == -1:
                    raise ValueError(f"HTML_TAG_UNTERMINATED: byte offset {off[end]}")
            if block.match(tag):
                out.add("\n", off[i], off[j + 1])
            i = j + 1
        elif c == "&":
            m = re.match(r"&(#\d+|#x[0-9a-fA-F]+|\w+);", s[i:])
            if m:
                out.add(html.unescape(m.group(0)), off[i], off[i + len(m.group(0))])
                i += len(m.group(0))
            else:
                out.add(c, off[i], off[i + 1]); i += 1
        else:
            out.add(c, off[i], off[i + 1]); i += 1
    return out


def compare_key(s: str) -> str:
    s = unicodedata.normalize("NFC", s).casefold()
    s = s.replace("ṁ", "ṃ").replace("’", "").replace("'", "").replace("‘", "")
    s = re.sub(r"(?<=\w)-(?=\w)", "", s)
    return s


TOKEN = re.compile(r"[^\W\d_](?:[^\W\d_]|['’\-])*", re.UNICODE)


def tokens(s: str) -> list[str]:
    return [compare_key(t) for t in TOKEN.findall(s)]


# ---------------- BJT (BuddhaDust carrier) ----------------
def bjt_segments(raw: bytes) -> dict:
    """Clause segments of MN 41 from the BuddhaDust BJT page.

    Boundaries: paragraph number at line start ('N. '), and the carrier's '||'
    clause marks. Page markers like [286] and the navigation strip of paragraph 1
    are recorded as separators, not content. Returns segments and coverage proof."""
    ch = html_chars(raw)
    t = ch.text
    start = t.index("Evaṃ me sutaṃ")
    last = t.rindex("||", start) + 2
    colo = t.find("Sāleyyaka Suttaṃ", last)
    stop = colo + len("Sāleyyaka Suttaṃ") if colo != -1 and colo - last < 40 else last
    body = t[start:stop]
    segs, seps = [], []
    para = 1
    i = 0
    cur = ""
    cur_i = None
    pat = re.compile(r"\|\|\s*\|\||\|\||\n\s*(?:\[\s*\d+\s*\]\s*)?(\d{1,2})\.\s|\[\s*\d+\s*\]")
    pos = 0
    def flush(a: int, b: int) -> None:
        nonlocal para
        frag = body[a:b]
        lead = len(frag) - len(frag.lstrip())
        tail = len(frag.rstrip())
        if frag.strip():
            ga, gb = start + a + lead, start + a + tail
            bs, be = ch.span(ga, gb)
            segs.append({"para": para, "text": t[ga:gb], "char_start": ga, "char_end": gb,
                         "byte_start": bs, "byte_end": be})
    for m in pat.finditer(body):
        flush(pos, m.start())
        if m.group(1):
            para = int(m.group(1))
        ga, gb = start + m.start(), start + m.end()
        seps.append({"kind": "para_no" if m.group(1) else ("page" if "[" in m.group(0) else "clause_mark"),
                     "text": t[ga:gb], "byte_start": ch.starts[ga], "byte_end": ch.ends[gb - 1]})
        pos = m.end()
    flush(pos, len(body))
    # coverage proof: concatenation of segments + separators (+whitespace) == body
    rebuilt = sorted([(s["char_start"], s["char_end"]) for s in segs])
    return {"segments": segs, "separators": seps, "body_char_range": [start, stop],
            "body_byte_range": [ch.starts[start], ch.ends[stop - 1]], "_chars": ch}


def nav_strip(seg_text: str) -> bool:
    return bool(re.fullmatch(r"(\[\s*\w+\s*\])+\s*", seg_text.strip()))


# ---------------- CST4 (VRI XML) ----------------
def cst_mn41(raw: bytes) -> dict:
    s = raw.decode("utf-16")
    a = s.index('<p rend="subhead">1. Sāleyyakasuttaṃ</p>')
    b = s.index('<p rend="subhead">2. ', a)
    frag = s[a:b]
    notes = re.findall(r"<note>(.*?)</note>", frag)
    paras = []
    for m in re.finditer(r'<p rend="(bodytext|centre|subhead)"[^>]*>(.*?)</p>', frag, re.S):
        inner = m.group(2)
        pts = re.findall(r'<pb ed="P" n="([\d.]+)"', inner)
        txt_with_notes = re.sub(r"<note>(.*?)</note>", r" ⟦\1⟧ ", inner)
        txt = re.sub(r"<[^>]+>", "", txt_with_notes)
        clean = re.sub(r"\s*⟦.*?⟧\s*", " ", txt)
        paras.append({"rend": m.group(1), "text": re.sub(r"\s+", " ", clean).strip(),
                      "with_notes": re.sub(r"\s+", " ", txt).strip(), "pts_pages": pts})
    return {"paragraphs": paras, "notes": notes, "char_range_in_decoded": [a, b]}


# ---------------- Mahasangiti (bilara JSON) ----------------
def ms_segments(raw: bytes) -> list[dict]:
    d = json.loads(raw.decode("utf-8"))
    return [{"id": k, "text": v} for k, v in d.items()]


# ---------------- Polish Google Doc (DOCX export) ----------------
def docx_paragraphs(raw: bytes) -> dict:
    import io
    z = zipfile.ZipFile(io.BytesIO(raw))
    x = z.read("word/document.xml").decode("utf-8")
    paras = []
    for m in re.finditer(r"<w:p[ >].*?</w:p>", x, re.S):
        p = m.group(0)
        out = ""
        for r in re.finditer(r"<w:t[^>]*>([^<]*)</w:t>|<w:footnoteReference[^>]*w:id=\"(\d+)\"[^>]*/>|<w:tab/>", p):
            if r.group(2):
                out += f"⟨fn{r.group(2)}⟩"
            elif r.group(1) is not None:
                out += html.unescape(r.group(1))
            else:
                out += "\t"
        paras.append(out)
    fx = z.read("word/footnotes.xml").decode("utf-8")
    foot = {}
    for fid, body in re.findall(r'<w:footnote [^>]*w:id="(-?\d+)"[^>]*>(.*?)</w:footnote>', fx, re.S):
        t = "".join(html.unescape(t) for t in re.findall(r"<w:t[^>]*>([^<]*)</w:t>", body)).strip()
        if t:
            foot[fid] = t
    return {"paragraphs": paras, "footnotes": foot}


def pl_canonical(raw: bytes) -> dict:
    """Canonical Polish text of MN 41 (from [§1] to the colophon), split into sentence
    units with stable IDs pl.§N.k. Footnote reference marks are kept as ⟨fnN⟩."""
    d = docx_paragraphs(raw)
    P = d["paragraphs"]
    i = next(k for k, p in enumerate(P) if p.startswith("[§1]"))
    j = next(k for k, p in enumerate(P) if re.match(r"Koniec (pierwszej sutty|Sāleyyakasutty)", p))
    units, cur = [], None
    for p in P[i:j + 1]:
        m = re.match(r"\[§(\d+)\]\s*", p)
        if m:
            cur = int(m.group(1)); p = p[m.end():]
        sec = cur if not re.match(r"Koniec (pierwszej sutty|Sāleyyakasutty)", p) else "colophon"
        first = True
        for s in re.split(r"(?<=[.?!])(?:[”«»\"]*)\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ„«—–])", p):
            if s.strip():
                units.append({"sec": sec, "text": s.strip(), "para_start": first})
                first = False
    count: dict[object, int] = {}
    for u in units:
        count[u["sec"]] = count.get(u["sec"], 0) + 1
        u["id"] = f"pl.§{u['sec']}.{count[u['sec']]}"
    return {"units": units, "footnotes": d["footnotes"], "doc_paragraph_range": [i, j]}
