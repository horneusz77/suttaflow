"""Minimal OOXML writer for the MN 41 RC document with NATIVE footnotes.

Styles follow SuttaFlow Standard §12/§14 (Merriweather 12 pt body, 1.15, 0/4 pt; Title 24;
Subtitle 14; Heading 1 18; Heading 2 14; footnotes 9.5 pt; shaded metadata block; parallel
block 10.5 pt italic). Converted to Google Docs, footnotes stay native.
Input spec: list of blocks {"t": kind, "runs": [...]} where a run is a string or
{"fn": "footnote text"} or {"b": "bold text"} or {"i": "italic text"}.
"""
from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'

STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {W}>
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Merriweather" w:hAnsi="Merriweather" w:cs="Merriweather"/><w:color w:val="3C3C3C"/><w:sz w:val="24"/><w:lang w:val="pl-PL"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="80" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="0" w:after="40"/></w:pPr><w:rPr><w:sz w:val="48"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="0" w:after="160"/></w:pPr><w:rPr><w:color w:val="666666"/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="200" w:after="80"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:sz w:val="36"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="40"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Meta"><w:name w:val="Meta"/><w:basedOn w:val="Normal"/><w:pPr><w:pBdr><w:left w:val="single" w:sz="24" w:space="6" w:color="999999"/></w:pBdr><w:shd w:val="clear" w:color="auto" w:fill="F1F1F1"/><w:spacing w:before="0" w:after="0"/><w:ind w:left="120"/></w:pPr><w:rPr><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Parallel"><w:name w:val="Parallel"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="360"/></w:pPr><w:rPr><w:i/><w:color w:val="555555"/><w:sz w:val="21"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="FootnoteText"><w:name w:val="footnote text"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="0"/></w:pPr><w:rPr><w:sz w:val="19"/></w:rPr></w:style>
<w:style w:type="character" w:styleId="FootnoteReference"><w:name w:val="footnote reference"/><w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>
</w:styles>"""

NUMBERING = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {W}><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>"""

STYLE_OF = {"title": "Title", "subtitle": "Subtitle", "h1": "Heading1", "h2": "Heading2", "p": "Normal",
            "meta": "Meta", "parallel": "Parallel", "li": "ListBullet"}


def _run(text: str, props: str = "") -> str:
    return f'<w:r>{"<w:rPr>" + props + "</w:rPr>" if props else ""}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def build(blocks: list[dict]) -> bytes:
    body: list[str] = []
    notes: list[str] = []
    for b in blocks:
        runs = []
        for r in b["runs"]:
            if isinstance(r, str):
                runs.append(_run(r))
            elif "b" in r:
                runs.append(_run(r["b"], "<w:b/>"))
            elif "i" in r:
                runs.append(_run(r["i"], "<w:i/>"))
            elif "fn" in r:
                nid = len(notes) + 1
                notes.append(f'<w:footnote w:id="{nid}"><w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr>'
                             f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>'
                             f'{_run(" " + r["fn"])}</w:p></w:footnote>')
                runs.append(f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteReference w:id="{nid}"/></w:r>')
        body.append(f'<w:p><w:pPr><w:pStyle w:val="{STYLE_OF[b["t"]]}"/></w:pPr>{"".join(runs)}</w:p>')
    doc = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {W}><w:body>{"".join(body)}'
           '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>')
    foot = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:footnotes {W}>'
            '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
            '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
            + "".join(notes) + "</w:footnotes>")
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
          '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
          '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
          '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
             '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>'
             '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/></Relationships>')
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in [("[Content_Types].xml", ct), ("_rels/.rels", rels), ("word/_rels/document.xml.rels", drels),
                           ("word/document.xml", doc), ("word/styles.xml", STYLES), ("word/numbering.xml", NUMBERING),
                           ("word/footnotes.xml", foot)]:
            zi = zipfile.ZipInfo(name, (2026, 10, 11, 0, 0, 0)); zi.create_system = 0  # Preserve the original Windows ZIP metadata on every host.
            zi.compress_type = zipfile.ZIP_DEFLATED; z.writestr(zi, data)
    return out.getvalue()
