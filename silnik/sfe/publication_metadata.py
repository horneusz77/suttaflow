"""Verify the completion day and the complete published bibliography (F028/F026).

N1 L158 / SF-RULE-OPS-004 and N1 L399 / SF-RULE-PUB-001/002.
This read-only adapter checks pinned bytes, exact native fields, complete Sources
sections and recorded visual evidence. It does not perform OCR, authenticate a
reviewer's identity, infer a completion time or grant publication authority.
The caller must first validate source_case with source_contract and exact-compare
the external PDF source-index pin with the source gate's verified index.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, datetime
import json
import re
import struct
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import zlib

from . import publication_inputs as PI
from . import release_evidence as RE
from . import source_contract as SC

READY = "METADATA_EVIDENCE_READY"
WARSAW = ZoneInfo("Europe/Warsaw")
COMPLETION_LABELS = {"Ukończenie:", "Data ukończenia:", "Ukończono:", "Wersja i data:"}
REVISION_LABELS = {"Rewizja:", "Data rewizji:"}
MONTH_NAMES = (
    ("jan", "january", "sty", "stycznia"),
    ("feb", "february", "lut", "lutego"),
    ("mar", "march", "mar", "marca"),
    ("apr", "april", "kwi", "kwietnia"),
    ("may", "may", "maj", "maja"),
    ("jun", "june", "cze", "czerwca"),
    ("jul", "july", "lip", "lipca"),
    ("aug", "august", "sie", "sierpnia"),
    ("sep", "september", "wrz", "września"),
    ("oct", "october", "paź", "października"),
    ("nov", "november", "lis", "listopada"),
    ("dec", "december", "gru", "grudnia"),
)
NUMERIC_DATE_PATTERN = re.compile(
    # Detection is broader than parsing: typographic separators, malformed
    # years and attached ISO times reach the bounded reader and produce HOLD.
    r"(?<!\w)\d+\s*[./‐‑‒–—―−／．－⁄∕-]\s*\d+"
    r"\s*[./‐‑‒–—―−／．－⁄∕-]\s*\d+[\w:]*"
)
GROUPS = (
    "Tekst źródłowy / podstawa Pali",
    "Kontrola tekstu Pali",
    "Przekłady porównawcze według pierwszeństwa",
    "Dodatkowa kontrola",
    "Słowniki",
    "Komentarz i teksty pomocnicze",
)
DATE_FORMATS = {
    "DATE_FORMAT_CUSTOM",
    "DATE_FORMAT_MONTH_DAY_ABBREVIATED",
    "DATE_FORMAT_MONTH_DAY_FULL",
    "DATE_FORMAT_MONTH_DAY_YEAR_ABBREVIATED",
    "DATE_FORMAT_ISO8601",
}


def _need(ok: Any, message: str) -> None:
    if not ok:
        raise RE.EvidenceError(message)


def _record(value: Any, required: set[str], optional: set[str] | None = None) -> dict:
    _need(isinstance(value, dict), "expected a record object")
    _need(
        required <= set(value) and not set(value) - required - (optional or set()),
        "record has absent or unknown fields: "
        + ", ".join(
            sorted(
                required - set(value) | (set(value) - required - (optional or set()))
            )
        ),
    )
    return value


def _records(value: Any, *, empty: bool = False) -> list[dict]:
    _need(
        isinstance(value, list)
        and (empty or value)
        and all(isinstance(v, dict) for v in value),
        "expected an array of record objects",
    )
    return value


def _strings(value: Any, *, empty: bool = False) -> list[str]:
    _need(
        isinstance(value, list)
        and (empty or value)
        and all(RE.nonempty(v) for v in value),
        "expected a string array",
    )
    _need(len(set(value)) == len(value), "duplicate string identifiers")
    return value


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict:
    obj: dict = {}
    for key, value in pairs:
        _need(key not in obj, "duplicate JSON object key")
        obj[key] = value
    return obj


def _read(root: Any, ref: Any, *, obj: bool = False) -> Any:
    _record(ref, {"path", "sha256", "bytes"})
    raw = RE.read_artifact(root, ref)
    if not obj:
        return raw
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    _need(isinstance(data, dict), "artifact must be a JSON object")
    return data


def _text(value: Any) -> str:
    _need(isinstance(value, str), "text is absent")
    return " ".join(value.split())


def _string(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RE.EvidenceError(what + " is absent")
    return value


def _day(value: Any) -> date:
    _need(
        isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value),
        "calendar day must be YYYY-MM-DD",
    )
    return date.fromisoformat(value)


def _auth(record: dict, actor: str | None = None) -> None:
    src = record.get("authenticated_source")
    if not isinstance(src, dict) or not all(
        RE.nonempty(src.get(k)) for k in ("actor_id", "uri", "record_id")
    ):
        raise RE.EvidenceError("original authenticated source provenance is absent")
    if actor is not None:
        _need(src["actor_id"] == actor, "recorded actor and source identity differ")


def _date_attestation(
    root: Any, ref: Any, subject: dict, kind: str, original_ref: dict | None = None
) -> dict:
    p = _read(root, ref, obj=True)
    _record(
        p,
        {
            "schema",
            "kind",
            "subject_id",
            "revision_id",
            "day",
            "zone",
            "basis",
            "recorded_at",
            "evidence_text",
            "authenticated_source",
        },
        {"event_at", "original_completion"},
    )
    _need(
        p["schema"] == "suttaflow-date-attestation-v2" and p["kind"] == kind,
        "completion/revision attestation kind differs",
    )
    _need(
        p["subject_id"] == subject["subject_id"] and RE.nonempty(p["revision_id"]),
        "date attestation identifies another work or no original revision",
    )
    _need(
        p["zone"] == "Europe/Warsaw",
        "completion/revision day is not based on Europe/Warsaw",
    )
    day = _day(p["day"])
    recorded = RE.timestamp(p["recorded_at"])
    _need(
        day <= recorded.astimezone(WARSAW).date(),
        "day is later than its recorded evidence",
    )
    _need(
        RE.nonempty(p["evidence_text"]),
        "original completion/revision evidence text absent",
    )
    _auth(p)
    if p["basis"] == "EXPLICIT_CALENDAR_DAY":
        _need(
            "event_at" not in p, "a date-only record must not invent a completion hour"
        )
    elif p["basis"] == "ACTUAL_COMPLETION_EVENT":
        event = RE.timestamp(p.get("event_at"))
        _need(
            event <= recorded and event.astimezone(WARSAW).date() == day,
            "actual event instant and Warsaw calendar day differ",
        )
    else:
        raise RE.EvidenceError(
            "date basis is not an explicit day or actual event; modifiedTime/chip encoding is insufficient"
        )
    if kind == "ORIGINAL_COMPLETION":
        _need(
            "original_completion" not in p,
            "original completion cannot reference a newer revision",
        )
    else:
        _need(
            p["revision_id"] == subject["revision_id"]
            and p.get("original_completion") == original_ref,
            "revision does not preserve the exact original completion evidence",
        )
    return p


def _pending(node: Any) -> bool:
    if isinstance(node, dict):
        return any(
            (k.startswith("suggested") and bool(v)) or _pending(v)
            for k, v in node.items()
        )
    return isinstance(node, list) and any(_pending(v) for v in node)


def _url(value: Any) -> str:
    _need(RE.nonempty(value), "link URL absent")
    parsed = urlparse(value)
    _need(
        parsed.scheme in {"http", "https"}
        and parsed.hostname
        and not parsed.username
        and not parsed.password,
        "public link is not an absolute HTTP(S) URL",
    )
    return value


def _paragraph(item: dict) -> dict:
    p = item.get("paragraph")
    if not isinstance(p, dict):
        return {"start": item.get("startIndex"), "unsupported": True}
    _need(
        type(item.get("startIndex")) is int and item["startIndex"] >= 0,
        "native paragraph start index absent",
    )
    _need(
        not _pending(p),
        "unresolved native suggestions make the displayed field ambiguous",
    )
    chunks: list[str] = []
    links: list[str] = []
    dates: list[dict] = []
    for e in _records(p.get("elements")):
        if isinstance(e.get("textRun"), dict):
            r = e["textRun"]
            _need(isinstance(r.get("content"), str), "native text run content absent")
            chunks.append(r["content"])
            style = r.get("textStyle", {})
            _need(isinstance(style, dict), "native text style is malformed")
            link = style.get("link", {})
            if link:
                _need(isinstance(link, dict), "native link shape is malformed")
                if not RE.nonempty(link.get("url")):
                    return {"start": item["startIndex"], "unsupported": True}
                links.append(_url(link["url"]))
        elif isinstance(e.get("richLink"), dict):
            r = e["richLink"].get("richLinkProperties", {})
            _need(
                isinstance(r, dict) and RE.nonempty(r.get("title")),
                "native richLink title absent",
            )
            chunks.append(r["title"])
            links.append(_url(r.get("uri")))
        elif isinstance(e.get("dateElement"), dict):
            r = e["dateElement"]
            props = r.get("dateElementProperties")
            _need(
                RE.nonempty(r.get("dateId"))
                and isinstance(props, dict)
                and RE.nonempty(props.get("displayText")),
                "native DateElement lacks readonly dateId/displayText",
            )
            dates.append(
                {"id": r["dateId"], "properties": props, "before": "".join(chunks)}
            )
            chunks.append(props["displayText"])
        else:
            # Do not silently discard a footnote, image, smart chip or unknown content
            # from the complete Sources/metadata field. Other document sections may
            # contain them and are not this adapter's content/FORMAT responsibility.
            return {"start": item["startIndex"], "unsupported": True}
    paragraph_style = p.get("paragraphStyle", {})
    _need(isinstance(paragraph_style, dict), "native paragraph style is malformed")
    return {
        "start": item["startIndex"],
        "text": "".join(chunks),
        "urls": list(dict.fromkeys(links)),
        "dates": dates,
        "style": paragraph_style.get("namedStyleType", "NORMAL_TEXT"),
        "bullet": p.get("bullet"),
        "unsupported": False,
    }


def _body(doc: dict, tab_id: Any) -> list[dict]:
    tabs: list[tuple[Any, Any]] = []

    def visit(items: Any) -> None:
        for tab in _records(items, empty=True):
            props = tab.get("tabProperties", tab)
            content = tab.get("documentTab", tab)
            _need(
                isinstance(props, dict) and isinstance(content, dict),
                "native tab shape invalid",
            )
            tabs.append((props.get("tabId"), content.get("body")))
            if tab.get("childTabs"):
                visit(tab["childTabs"])

    if doc.get("tabs"):
        visit(doc["tabs"])
        _need(RE.nonempty(tab_id), "multi-tab native input needs an explicit tab ID")
        _need(
            all(RE.nonempty(t[0]) for t in tabs)
            and len({t[0] for t in tabs}) == len(tabs),
            "native tab IDs absent or duplicated",
        )
        matches = [b for tid, b in tabs if tid == tab_id]
        _need(len(matches) == 1, "exact native tab is absent")
        body = matches[0]
    else:
        _need(tab_id is None, "legacy body cannot prove a named tab")
        body = doc.get("body")
    _need(isinstance(body, dict), "full native body absent")
    rows = [
        _paragraph(p) for p in _records(body.get("content")) if "sectionBreak" not in p
    ]
    starts = [r["start"] for r in rows]
    _need(
        all(type(n) is int for n in starts)
        and len(set(starts)) == len(starts)
        and starts == sorted(starts),
        "full native paragraph positions are absent, duplicated or out of order",
    )
    return rows


def _row(rows: list[dict], start: Any) -> dict:
    _need(type(start) is int, "native field locator is not an integer paragraph start")
    found = [r for r in rows if r["start"] == start]
    _need(
        len(found) == 1 and not found[0]["unsupported"],
        "complete native field is absent or has unsupported content",
    )
    return found[0]


def _named_date_tokens(text: str) -> list[str]:
    """Use identical punctuation/case normalization for detection and parsing."""
    return text.casefold().replace(",", "").replace(".", "").split()


def _display_day(text: str, expected: date) -> date:
    """Bounded visible-date reader; unsupported locales/formats return HOLD.

    It does not impose a new public date style. ISO and existing EN/PL chips are
    supported. A year omitted by Docs' explicit month/day format uses the pinned
    encoded year, never a file's modification date.
    """
    value = _text(text).strip().rstrip(".")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return _day(value)
    numbers = re.fullmatch(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", value)
    if numbers:
        return date(int(numbers[3]), int(numbers[2]), int(numbers[1]))
    tokens = _named_date_tokens(value)
    _need(len(tokens) != 3 or tokens[2].isdigit(), "visible year is malformed")
    for m, names in enumerate(MONTH_NAMES, 1):
        if len(tokens) not in (2, 3):
            continue
        number = (
            tokens[1] if tokens[0] in names and tokens[1].isdigit()
            else tokens[0] if tokens[0].isdigit() and tokens[1] in names
            else None
        )
        if number is not None:
            year = int(tokens[2]) if len(tokens) == 3 else expected.year
            day = int(number)
            _need(
                1 <= year <= 9999 and 1 <= day <= 31,
                "visible calendar day/year is out of range",
            )
            return date(year, m, day)
    raise RE.EvidenceError(
        "visible native date format/locale is outside the bounded ISO/EN/PL reader"
    )


def _current_date_candidates(text: str, expected: date) -> Iterator[str]:
    """Yield complete candidate values, without selecting an agreeable prefix.

    Named dates use the reader's actual token normalization, including commas
    or periods within tokens and punctuation-only intervening tokens. Unknown
    month words with a year and malformed numeric suffixes still reach HOLD.
    This recognizes bounded date shapes, not arbitrary natural-language dates.
    """
    numeric = list(NUMERIC_DATE_PATTERN.finditer(text))
    named_spans: list[tuple[int, int]] = []
    tokens = []
    for match in re.finditer(r"\S+", text):
        normalized = _named_date_tokens(match[0])
        if normalized:
            tokens.append((match, normalized[0]))
    months = {name for aliases in MONTH_NAMES for name in aliases}

    def number_shaped(value: str) -> bool:
        value = value.lstrip("([{+-−")
        return bool(value) and value[0].isdigit()

    consumed_until = 0
    for i in range(len(tokens) - 1):
        first, a = tokens[i]
        if first.start() < consumed_until:
            continue
        second, b = tokens[i + 1]
        known = (number_shaped(a) and b in months) or (
            a in months and number_shaped(b)
        )
        has_year = i + 2 < len(tokens) and number_shaped(tokens[i + 2][1])
        unknown = has_year and (
            (number_shaped(a) and b.isalpha())
            or (a.isalpha() and number_shaped(b))
        )
        if known or unknown:
            end = tokens[i + 2][0].end() if has_year else second.end()
            candidate = text[first.start() : end]
            # A numeric-looking part can belong to a valid named spelling
            # (e.g. '0.1.2 Oct 2.0.2.6'). Prefer the actual reader's grammar.
            # Conversely, a complete numeric date before another named date
            # must not be misread as that named date's day token.
            try:
                _display_day(candidate, expected)
            except (RE.EvidenceError, ValueError):
                if any(
                    n.start() == first.start() and n.end() == first.end()
                    for n in numeric
                ):
                    continue
            consumed_until = end
            named_spans.append((first.start(), end))
            yield candidate
    for match in numeric:
        if not any(a <= match.start() and match.end() <= b for a, b in named_spans):
            yield match[0]


def _chip_day(chip: dict, day: str) -> str:
    props = chip["properties"]
    _need(
        props.get("dateFormat", "DATE_FORMAT_MONTH_DAY_YEAR_ABBREVIATED")
        in DATE_FORMATS,
        "unknown Docs dateFormat enum",
    )
    _need(
        props.get("timeFormat", "TIME_FORMAT_DISABLED") == "TIME_FORMAT_DISABLED",
        "technical encoding hour is displayed as a completion/revision time",
    )
    stamp = props.get("timestamp")
    _need(RE.nonempty(stamp), "date chip encoding timestamp absent")
    encoded = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    _need(encoded.tzinfo is not None, "date chip timestamp must be timezone-aware")
    zone = props.get("timeZoneId", "Etc/UTC")
    if zone == "etc/UTC":
        zone = "Etc/UTC"
    _need(RE.nonempty(zone), "native date timezone is invalid")
    actual = encoded.astimezone(ZoneInfo(zone)).date()
    _need(actual == _day(day), "date chip encodes another calendar day")
    _need(
        _display_day(props["displayText"], actual) == actual,
        "readonly native date display differs from the completion day",
    )
    return props["displayText"]


def _current_date_fields(row: dict, day: str, *, revision: bool) -> None:
    """Check all values in the selected paragraph's current labelled fields.

    A completion selector may not choose one chip while a conflicting chip or
    supported visible date remains in that field. Revision labels delimit fields;
    other labelled metadata (such as history) also delimit the current value.
    Other document paragraphs, including historical dates, are not reclassified.
    """
    labels = REVISION_LABELS if revision else COMPLETION_LABELS
    all_labels = sorted(COMPLETION_LABELS | REVISION_LABELS, key=len, reverse=True)
    text = row["text"]
    fields = list(
        re.finditer(
            r"(?<!\w)(?:" + "|".join(re.escape(label) for label in all_labels) + ")",
            text,
        )
    )
    boundaries = {m.start() for m in fields}
    # A separately labelled non-date field is not part of a completion value.
    boundaries.update(
        m.start(1) for m in re.finditer(r"(?:^|[·;|\n])\s*([^:·;|\n]+:)", text)
    )
    for field in fields:
        if field[0] not in labels:
            continue
        end = min((n for n in boundaries if n > field.start()), default=len(text))
        start = field.end()
        chips = [d for d in row["dates"] if start <= len(d["before"]) < end]
        plain = list(text[start:end])
        for chip in chips:
            _chip_day(chip, day)
            a = len(chip["before"]) - start
            b = a + len(chip["properties"]["displayText"])
            plain[a:b] = " " * (b - a)
        expected = _day(day)
        for visible in _current_date_candidates("".join(plain), expected):
            _need(
                _display_day(visible, expected) == expected,
                "current completion/revision field contains conflicting days",
            )
        # A date-free 'Wersja i data: r2' prefix is only a version wrapper.
        # Actual completion/revision presence and the selected chip are checked
        # separately below, so the empty wrapper cannot satisfy a date gate.


def _native_day(
    rows: list[dict], selector: Any, day: str, *, revision: bool = False
) -> str:
    _record(selector, {"paragraph_start", "date_id", "label"})
    labels = REVISION_LABELS if revision else COMPLETION_LABELS
    _need(
        selector["label"] in labels,
        "date selector does not identify a completion/revision field",
    )
    row = _row(rows, selector["paragraph_start"])
    _current_date_fields(row, day, revision=revision)
    if revision and selector["date_id"] is None:
        found = re.findall(
            re.escape(selector["label"]) + r"\s*(\d{4}-\d{2}-\d{2})(?!\d)", row["text"]
        )
        _need(
            found == [day],
            "separate native revision-date field is absent or another day",
        )
        return found[0]
    ids = [
        d
        for r in rows
        if not r["unsupported"]
        for d in r["dates"]
        if d["id"] == selector["date_id"]
    ]
    matches = [d for d in row["dates"] if d["id"] == selector["date_id"]]
    _need(
        len(ids) == len(matches) == 1,
        "actual date chip ID is absent or duplicated; textRun is not a chip",
    )
    chip = matches[0]
    _need(
        chip["before"].rstrip().endswith(selector["label"]),
        "chip is not in the labelled completion/revision field",
    )
    return _chip_day(chip, day)


def _dates(root: Any, m: dict, subject: dict, doc: dict, rows: list[dict]) -> dict:
    d = _record(
        m["dates"],
        {
            "original_completion",
            "revision",
            "filename_date_span",
            "native_completion",
            "native_revision",
        },
    )
    original = _date_attestation(
        root, d["original_completion"], subject, "ORIGINAL_COMPLETION"
    )
    revised = None
    if d["revision"] is not None:
        revised = _date_attestation(
            root, d["revision"], subject, "REVISION", d["original_completion"]
        )
        _need(
            _day(revised["day"]) >= _day(original["day"]),
            "revision precedes original completion",
        )
    else:
        _need(
            original["revision_id"] == subject["revision_id"]
            and d["native_revision"] is None,
            "new revision needs a separate date and the original completion evidence",
        )
    span = d["filename_date_span"]
    title = _string(doc.get("title"), "actual native filename")
    _need(
        isinstance(span, list) and len(span) == 2 and all(type(n) is int for n in span),
        "actual native filename or exact filename day span absent",
    )
    a, b = span
    _need(
        0 <= a < b <= len(title) and title[a:b] == original["day"],
        "actual file name does not preserve the original Warsaw completion day",
    )
    naming_dates = list(re.finditer(r"\[[^\[\]\n]+,\s*(\d{4}-\d{2}-\d{2})\]", title))
    _need(
        len(naming_dates) == 1 and list(naming_dates[0].span(1)) == span,
        "selected date is not the original tool/date field of the active file naming convention",
    )
    completion_display = _native_day(rows, d["native_completion"], original["day"])
    revision_display = (
        _native_day(rows, d["native_revision"], revised["day"], revision=True)
        if revised
        else None
    )
    if revised:
        _need(
            d["native_revision"]["date_id"] != d["native_completion"]["date_id"],
            "revision reuses the original completion field",
        )
    return {
        "completion_date": original["day"],
        "revision_date": revised["day"] if revised else None,
        "completion_display_text": completion_display,
        "revision_display_text": revision_display,
        "completion_basis": original["basis"],
    }


def _proof(
    root: Any, index: dict, key: Any, kind: str, subject: dict, *, partial: bool = False
) -> dict:
    _need(RE.nonempty(key) and key in index, "exact source evidence key is absent")
    p = _read(root, index[key], obj=True)
    RE.binding(p, subject, partial=partial)
    _need(p.get("kind") == kind, "source evidence kind differs")
    _auth(p)
    return p


def _link_proof(
    root: Any, index: dict, key: Any, subject: dict, source_id: str
) -> dict:
    p = _proof(root, index, key, "PUBLIC_LINK_CHECK", subject, partial=True)
    _need(
        p.get("source_id") == source_id
        and p.get("is_official") is True
        and p.get("is_public") is True
        and p.get("reachable") is True,
        "actual official public link check differs",
    )
    _url(p.get("url"))
    RE.timestamp(p.get("checked_at"))
    return p


def _controller_order(
    root: Any, case: dict, index: dict, subject: dict, sources: dict
) -> None:
    contract = json.loads(SC.CONTRACT_PATH.read_text(encoding="utf-8"))
    _need(
        tuple(contract["public_source_group_order"]) == GROUPS,
        "local source group contract differs",
    )
    profile = contract["profiles"].get(case.get("profile"))
    _need(isinstance(profile, dict), "unknown verified source profile")
    if case["profile"] == "VINAYA_OTHER":
        # N1 assigns a subject-specific witness/translator plan here, not the MN
        # Pali/EN chain. Its adequacy and evidence were checked by SC, not invented.
        return
    if case["profile"] == "KN_OTHER":
        proof = _proof(
            root,
            index,
            case.get("other_kn_owner_contract_ref"),
            "KN_SOURCE_CONTRACT",
            subject,
        )
        _need(
            proof.get("status") == "APPROVED"
            and proof.get("actor_kind") == "HUMAN"
            and proof.get("actor_role") == "OWNER",
            "KN source profile is not the previously verified scoped owner contract",
        )
        profile = _record(proof.get("source_profile"), {"sequence", "philological"})
    sequence = profile["sequence"]
    _need(isinstance(sequence, list), "profile source sequence absent")
    ranks: dict[str, int] = {}
    for i, stage in enumerate(sequence):
        for role in _strings(stage):
            ranks.setdefault(role, i)
    for role in _strings(profile["philological"], empty=True):
        ranks.setdefault(role, len(sequence))
    actual = []
    for item in case["public_sources"]:
        if item["group"] == GROUPS[2]:
            role = sources[item["source_id"]]["profile_role"]
            _need(
                role in ranks,
                "bibliographic controller has no priority in the verified source profile",
            )
            actual.append(ranks[role])
    _need(
        actual == sorted(actual),
        "comparison bibliography reverses the active controller priority",
    )


def _expected_bibliography(
    root: Any, m: dict, case: dict, index: dict, subject: dict
) -> tuple[list[dict], str]:
    RE.binding(case, subject)
    _need(
        case.get("intended_publication") is True
        and type(case.get("is_synthetic")) is bool
        and case["is_synthetic"] == m["is_synthetic"],
        "source case publication/synthetic scope differs",
    )
    sources: dict[str, dict] = {}
    for s in _records(case.get("sources")):
        sid = _string(s.get("source_id"), "source inventory ID")
        _need(sid not in sources, "source inventory ID duplicated")
        sources[sid] = s
    _need(isinstance(case.get("basis"), dict), "verified actual source basis absent")
    public = _records(case.get("public_sources"))
    entries = _records(m["bibliography"].get("entries"))
    _need(
        [r.get("source_id") for r in entries] == [r.get("source_id") for r in public],
        "render inventory omits, adds, duplicates or reorders a registered public source",
    )
    ids = _strings([r.get("source_id") for r in public])
    _need(set(ids) <= set(sources), "unknown public source")
    _need(
        {sid for sid, s in sources.items() if s.get("used") is True} <= set(ids),
        "an actually used source/intermediary/helper is absent from the full bibliography",
    )
    orders = []
    expected: list[dict] = []
    for entry, item in zip(entries, public):
        _record(
            entry,
            {
                "source_id",
                "represented_scope",
                "scope_note",
                "text",
                "additional_link_check_refs",
            },
            {"scope_note_separator"},
        )
        sid = entry["source_id"]
        s = sources[sid]
        units = _strings(item.get("represented_scope"))
        read_scope = _strings(s.get("read_scope"))
        _need(
            s.get("read_state") == "READ" and set(units) <= set(read_scope),
            "listed source is unread or exaggerates its read scope",
        )
        if s.get("used") is True:
            _need(
                set(units) == set(read_scope),
                "used source bibliography omits its represented read scope",
            )
        _need(
            entry["represented_scope"] == units,
            "rendered citation scope differs from the verified read register",
        )
        group = item.get("group")
        _need(group in GROUPS, "unknown public source group")
        role_group = (
            0
            if sid == case["basis"].get("source_id")
            else 1
            if s.get("evidence_kind") == "CONTROL_PALI"
            else 4
            if s.get("evidence_kind") == "LEXICON"
            else 3
            if s.get("evidence_kind") == "ADDITIONAL_VERIFIER"
            else 5
            if s.get("evidence_kind") in {"COMMENTARY", "PARALLEL"}
            else 2
        )
        _need(
            group == GROUPS[role_group],
            "bibliographic group differs from actual source role",
        )
        orders.append(role_group)
        citation = _string(item.get("citation"), "full bibliographic citation")
        attribution = item.get("attribution", "")
        _need(
            isinstance(attribution, str) and isinstance(entry["scope_note"], str),
            "attribution/scope note is malformed",
        )
        if s.get("profile_role") == "DPD":
            _need(
                RE.nonempty(s.get("author_or_editor"))
                and s["author_or_editor"] in attribution
                and "CC BY-NC-SA 4.0" in attribution,
                "DPD author or exact licence attribution absent",
            )
        parts = [citation.strip()]
        if attribution.strip() and attribution not in citation:
            parts.append(attribution.strip())
        rendered = " — ".join(parts)
        separator = entry.get("scope_note_separator", " — ")
        _need(
            separator in (" — ", " · ", "; ", ". "),
            "unsupported explicit scope-note separator",
        )
        if entry["scope_note"].strip():
            rendered += separator + entry["scope_note"].strip()
        _need(
            _text(entry["text"]) == _text(rendered),
            "render text omits or rewrites citation, attribution or scope note",
        )
        urls = []
        if item.get("book_citation_instead_of_unofficial_link") is True:
            _need(
                not item.get("official_url")
                and all(
                    RE.nonempty(s.get(k)) and s[k] in citation
                    for k in ("title", "author_or_editor", "edition")
                ),
                "private/unofficial copy is exposed or lacks the actual book edition citation",
            )
        else:
            url = _url(item.get("official_url"))
            p = _link_proof(
                root, index, item.get("link_check_evidence_ref"), subject, sid
            )
            _need(
                p["url"] == url and p["checked_at"] == item.get("link_checked_at"),
                "source link target/date differs from its real check",
            )
            urls.append(url)
        for key in _strings(entry["additional_link_check_refs"], empty=True):
            urls.append(_link_proof(root, index, key, subject, sid)["url"])
        # Rights can require more than a public-source author's name. Preserve the
        # actual attribution wording from every applicable verified clearance.
        for key in _strings(case.get("rights_evidence_refs"), empty=True):
            right = _proof(root, index, key, "SOURCE_RIGHTS_CLEARANCE", subject)
            if right.get("source_id") == sid:
                _need(
                    RE.nonempty(right.get("attribution"))
                    and _text(right["attribution"]) in _text(entry["text"]),
                    "rendered bibliography omits an applicable rights attribution",
                )
        expected.append(
            {
                "source_id": sid,
                "group": group,
                "text": _text(entry["text"]),
                "urls": sorted(set(urls)),
            }
        )
    _need(
        orders == sorted(orders), "bibliographic source groups are out of active order"
    )
    _controller_order(root, case, index, subject, sources)
    disclosure = _proof(
        root,
        index,
        public[-1].get("disclosure_evidence_ref"),
        "PUBLIC_SOURCE_DISCLOSURE",
        subject,
    )
    RE.timestamp(disclosure.get("at"))
    _need(
        type(disclosure.get("ai_used")) is bool
        and disclosure.get("human_review_status")
        in {"NO_HUMAN_REVIEW", "PARTIAL_HUMAN_REVIEW", "FULL_HUMAN_REVIEW", "UNKNOWN"}
        and RE.nonempty(disclosure.get("text")),
        "final verified AI/human disclosure is absent",
    )
    return expected, _text(disclosure["text"])


def _native_bibliography(
    rows: list[dict], heading_start: Any, expected: list[dict], disclosure: str
) -> list[dict]:
    heads = [r for r in rows if not r["unsupported"] and _text(r["text"]) == "Źródła"]
    _need(
        len(heads) == 1
        and heads[0]["start"] == heading_start
        and heads[0]["style"] == "HEADING_2",
        "one complete K1 native Sources heading is not identified",
    )
    start = rows.index(heads[0]) + 1
    end = len(rows)
    for i in range(start, len(rows)):
        r = rows[i]
        if not r["unsupported"] and (
            r["style"] in {"HEADING_1", "HEADING_2"}
            or (r["style"] == "HEADING_3" and _text(r["text"]) == "Metryka przekładu")
        ):
            end = i
            break
    actual = []
    for r in rows[start:end]:
        _need(not r["unsupported"], "full Sources section contains unaccounted content")
        if _text(r["text"]):
            _need(not r["dates"], "date chip is not a bibliography citation")
            actual.append(
                {
                    "text": _text(r["text"]),
                    "urls": sorted(r["urls"]),
                    "bullet": r["bullet"],
                }
            )
    _compare_blocks(actual, expected, disclosure, native=True)
    return [{"text": r["text"], "urls": r["urls"]} for r in actual]


def _compare_blocks(
    actual: list[dict], expected: list[dict], disclosure: str, *, native: bool = False
) -> None:
    pos = 0
    previous = None
    for row in expected:
        if (
            row["group"] != previous
            and pos < len(actual)
            and actual[pos]["text"] == row["group"]
        ):
            _need(not actual[pos]["urls"], "group label has an unexpected hyperlink")
            pos += 1
        _need(
            pos < len(actual), "actual bibliography omits a source or final disclosure"
        )
        got = actual[pos]
        _need(
            got["text"] == row["text"] and got["urls"] == row["urls"],
            "actual full bibliography text/link differs for source " + row["source_id"],
        )
        if native:
            _need(
                isinstance(got.get("bullet"), dict)
                and RE.nonempty(got["bullet"].get("listId")),
                "native bibliography source is not an actual list item",
            )
        pos += 1
        previous = row["group"]
    _need(
        pos + 1 == len(actual)
        and actual[pos]["text"] == disclosure
        and not actual[pos]["urls"],
        "full bibliography must end with its exact disclosure; extra/duplicate/omitted paragraphs are not ignored",
    )


def _channel_blocks(raw: bytes, fmt: str) -> list[dict]:
    text = raw.decode("utf-8")
    lines = text.splitlines()
    if fmt == "MARKDOWN":
        heads = [
            (i, len(m[1]))
            for i, line in enumerate(lines)
            if (m := re.fullmatch(r"(#{1,6})\s+Źródła\s*", line))
        ]
    else:
        _need(fmt == "PLAIN_TEXT", "unsupported actual channel representation")
        heads = [(i, 0) for i, line in enumerate(lines) if line.strip() == "Źródła"]
    _need(len(heads) == 1, "full channel needs exactly one Sources heading")
    start, level = heads[0]
    selected = []
    for line in lines[start + 1 :]:
        heading = (
            re.fullmatch(r"(#{1,6})\s+(.+?)\s*", line) if fmt == "MARKDOWN" else None
        )
        if line.strip() == "Metryka przekładu" or (
            heading and (len(heading[1]) <= level or heading[2] == "Metryka przekładu")
        ):
            break
        selected.append(line)
    blocks = []
    for line in selected:
        value = line.strip()
        if not value:
            continue
        urls: list[str] = []
        value = re.sub(r"^(?:[-*+] |\d+[.)] )", "", value)
        if fmt == "MARKDOWN":
            value = re.sub(r"^#{1,6}\s+", "", value)
            value = re.sub(r"^(?:[-*+] |\d+[.)] )", "", value)

            def link(match: re.Match) -> str:
                urls.append(_url(match[2]))
                return match[1]

            value = re.sub(r"\[([^\]\n]+)\]\((https?://[^\s()]+)\)", link, value)
            _need(
                not re.search(r"\[[^\]]*\]\(|<[^>]*>|!\[", value),
                "unsupported/hidden channel link or image markup",
            )
            if (value.startswith("**") and value.endswith("**")) or (
                value.startswith("__") and value.endswith("__")
            ):
                value = value[2:-2]
        urls.extend(_url(u) for u in re.findall(r"https?://[^\s<>]+", value))
        blocks.append({"text": _text(value), "urls": sorted(set(urls))})
    return blocks


def _channels(
    root: Any, m: dict, requested: Any, expected: list[dict], disclosure: str
) -> None:
    _need(
        isinstance(requested, (tuple, list)),
        "requested channels must come from the independently supplied scope",
    )
    names = _strings(list(requested), empty=True)
    channels = _records(m["channels"], empty=True)
    ids = _strings([c.get("channel_id") for c in channels], empty=True)
    _need(
        set(ids) == set(names),
        "prepared channel inventory differs from the independent requested scope",
    )
    for c in channels:
        _record(c, {"channel_id", "artifact", "format"})
        _compare_blocks(
            _channel_blocks(_read(root, c["artifact"]), c["format"]),
            expected,
            disclosure,
        )


def _png_palette_row(
    row: bytearray, previous: bytes, kind: int, width: int, depth: int, entries: int
) -> bytes:
    """Undo filtering before checking actual palette indices, ignoring pad bits."""
    for i, value in enumerate(row):
        left = row[i - 1] if i else 0
        up = previous[i] if previous else 0
        corner = previous[i - 1] if previous and i else 0
        if kind == 1:
            value += left
        elif kind == 2:
            value += up
        elif kind == 3:
            value += (left + up) // 2
        elif kind == 4:
            p = left + up - corner
            a, b, c = abs(p - left), abs(p - up), abs(p - corner)
            value += left if a <= b and a <= c else up if b <= c else corner
        row[i] = value & 255
    mask = (1 << depth) - 1
    for pixel in range(width):
        index = (row[pixel * depth // 8] >> (8 - depth - pixel * depth % 8)) & mask
        _need(index < entries, "PNG pixel references an absent palette entry")
    return bytes(row)


def _png_pixels(
    parts: list[memoryview],
    width: int,
    height: int,
    depth: int,
    color: int,
    interlace: int,
    palette_entries: int | None,
) -> None:
    """Validate the complete static image without materializing its full raster.

    zlib output is bounded by the exact scanline layout plus one excess byte.
    Non-indexed pixel bit patterns are all valid once sizes/filters are valid;
    indexed pixels require inverse filtering and two rows of palette storage.
    Adam7 resets previous-row filtering separately for every nonempty pass.
    """
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    passes = (
        ((0, 0, 1, 1),)
        if not interlace
        else (
            (0, 0, 8, 8),
            (4, 0, 8, 8),
            (0, 4, 4, 8),
            (2, 0, 4, 4),
            (0, 2, 2, 4),
            (1, 0, 2, 2),
            (0, 1, 1, 2),
        )
    )
    layout = []
    for x, y, dx, dy in passes:
        w = max(0, (width - x + dx - 1) // dx)
        h = max(0, (height - y + dy - 1) // dy)
        if w and h:
            layout.append((w, h, (w * channels * depth + 7) // 8))
    expected = sum(h * (row_bytes + 1) for _, h, row_bytes in layout)

    def inflate() -> Iterator[bytes]:
        decoder = zlib.decompressobj()
        produced = 0
        try:
            for part in parts:
                if decoder.eof:
                    # PNG 3 11.2.3: unused bytes after the complete image stream
                    # in the final IDAT are ignored; they are not a new image.
                    continue
                pending = bytes(part)
                while True:
                    limit = min(65536, expected - produced + 1)
                    block = decoder.decompress(pending, limit)
                    produced += len(block)
                    _need(
                        produced <= expected,
                        "PNG inflated data exceeds its image layout",
                    )
                    if block:
                        yield block
                    pending = decoder.unconsumed_tail
                    if decoder.eof or (not pending and len(block) < limit):
                        break
            _need(decoder.eof, "PNG zlib stream or checksum trailer is incomplete")
            _need(
                produced == expected, "PNG inflated data does not fill its image layout"
            )
        except zlib.error as exc:
            raise RE.EvidenceError(
                "PNG image data cannot be decompressed: " + str(exc)
            ) from exc

    stream = iter(inflate())
    block = b""
    offset = 0

    def consume(count: int, *, keep: bool = False) -> bytes:
        nonlocal block, offset
        retained = bytearray()
        while count:
            if offset == len(block):
                block = next(stream, b"")
                offset = 0
                _need(block, "PNG scanline data is truncated")
            n = min(count, len(block) - offset)
            if keep:
                retained.extend(block[offset : offset + n])
            offset += n
            count -= n
        return bytes(retained)

    for w, h, row_bytes in layout:
        previous = b""
        for _ in range(h):
            kind = consume(1, keep=True)[0]
            _need(kind <= 4, "PNG scanline has an unknown filter type")
            if color == 3:
                if palette_entries is None:
                    raise RE.EvidenceError("PNG indexed image lacks its palette")
                previous = _png_palette_row(
                    bytearray(consume(row_bytes, keep=True)),
                    previous,
                    kind,
                    w,
                    depth,
                    palette_entries,
                )
            else:
                consume(row_bytes)
    _need(offset == len(block), "PNG has surplus decoded image bytes")
    _need(next(stream, None) is None, "PNG has surplus decoded image data")


def _png(raw: bytes) -> None:
    """Check PNG critical structure, checksums and actual static-image decoding."""
    _need(
        raw.startswith(b"\x89PNG\r\n\x1a\n"), "viewed-page artifact is not a PNG render"
    )
    pos = 8
    header = None
    palette_entries = None
    parts: list[memoryview] = []
    data_closed = False
    ended = False
    valid_depths = {
        0: (1, 2, 4, 8, 16),
        2: (8, 16),
        3: (1, 2, 4, 8),
        4: (8, 16),
        6: (8, 16),
    }
    while pos < len(raw):
        _need(pos + 12 <= len(raw), "PNG chunk is truncated")
        length = struct.unpack(">I", raw[pos : pos + 4])[0]
        _need(
            length <= 2**31 - 1 and pos + length + 12 <= len(raw),
            "PNG chunk length is invalid",
        )
        kind = raw[pos + 4 : pos + 8]
        _need(
            all(65 <= b <= 90 or 97 <= b <= 122 for b in kind),
            "PNG chunk type is invalid",
        )
        payload = memoryview(raw)[pos + 8 : pos + length + 8]
        crc = struct.unpack(">I", raw[pos + length + 8 : pos + length + 12])[0]
        _need(
            zlib.crc32(payload, zlib.crc32(kind)) == crc,
            "PNG render checksum is invalid",
        )
        _need(header is not None or kind == b"IHDR", "PNG first chunk is not IHDR")
        if kind == b"IHDR":
            _need(
                header is None and pos == 8 and length == 13,
                "PNG IHDR is duplicated or malformed",
            )
            header = struct.unpack(">IIBBBBB", payload)
            width, height, depth, color, compression, filtering, interlace = header
            _need(
                0 < width <= 2**31 - 1 and 0 < height <= 2**31 - 1,
                "PNG dimensions are invalid",
            )
            _need(
                depth in valid_depths.get(color, ()),
                "PNG color type/bit depth is invalid",
            )
            _need(
                compression == filtering == 0 and interlace in (0, 1),
                "PNG compression/filter/interlace method is unsupported",
            )
        elif kind == b"PLTE":
            _need(
                not parts and palette_entries is None and color in (2, 3, 6),
                "PNG palette position/type/count is invalid",
            )
            _need(
                0 < length <= 768 and length % 3 == 0,
                "PNG palette does not contain RGB triplets",
            )
            palette_entries = length // 3
            _need(
                color != 3 or palette_entries <= 1 << depth,
                "PNG palette exceeds the index bit depth",
            )
        elif kind == b"IDAT":
            _need(not data_closed, "PNG IDAT chunks are not consecutive")
            _need(
                color != 3 or palette_entries is not None,
                "PNG indexed image lacks PLTE",
            )
            parts.append(payload)
        elif kind == b"IEND":
            _need(
                parts and length == 0 and pos + 12 == len(raw),
                "PNG IEND/data are incomplete or followed by extra chunks",
            )
            ended = True
        else:
            _need(kind[0] & 32, "PNG has an unknown critical chunk")
        if parts and kind != b"IDAT":
            data_closed = True
        pos += length + 12
    _need(
        header is not None and ended and parts,
        "PNG critical chunk inventory is incomplete",
    )
    _png_pixels(parts, width, height, depth, color, interlace, palette_entries)


def _pdf(
    root: Any,
    report: dict,
    subject: dict,
    native_ref: dict,
    m: dict,
    dates: dict,
    blocks: list[dict],
    ids: list[str],
) -> None:
    RE.binding(report, subject)
    _need(
        report.get("kind") == "FORMAT_PDF"
        and report.get("result") in {"PASS", "PASS_WITH_NOTES"},
        "current FORMAT_PDF report is absent",
    )
    raw = _read(root, report.get("artifact"))
    count = PI.pdf_page_count(raw)
    _need(
        report.get("page_count") == count
        and report.get("pages_viewed") == list(range(1, count + 1)),
        "PDF page tree and recorded complete view differ",
    )
    _need(
        report.get("exported_from_document_revision_id") == m["native"]["revision_id"],
        "PDF uses a stale native revision",
    )
    p = _record(
        report["publication_metadata"].get("visual_review"),
        {
            "kind",
            "result",
            "native_artifact",
            "pdf_artifact",
            "document_id",
            "document_revision_id",
            "completion_date",
            "revision_date",
            "completion_display_text",
            "revision_display_text",
            "completion_page",
            "revision_page",
            "sources_pages",
            "source_ids",
            "bibliography_blocks",
            "rendered_pages",
            "completed_at",
            "actor",
            "evidence_text",
            "authenticated_source",
        },
    )
    _need(
        p["kind"] == "PUBLICATION_METADATA_VISUAL_REVIEW" and p["result"] == "PASS",
        "actual visible metadata review is absent",
    )
    _need(
        p["native_artifact"] == native_ref
        and p["pdf_artifact"] == report["artifact"]
        and p["document_id"] == m["native"]["document_id"]
        and p["document_revision_id"] == m["native"]["revision_id"],
        "visible review pins another actual native/PDF artifact",
    )
    for key in (
        "completion_date",
        "revision_date",
        "completion_display_text",
        "revision_display_text",
    ):
        _need(p[key] == dates[key], "visibly reviewed exported " + key + " differs")
    _need(
        p["source_ids"] == ids and p["bibliography_blocks"] == blocks,
        "PDF visual review does not account for the complete actual bibliography",
    )
    _need(RE.nonempty(p["evidence_text"]), "actual page-view evidence text absent")
    actor = _record(p["actor"], {"id", "model", "context_id", "kind"})
    _need(
        all(RE.nonempty(actor[k]) for k in ("id", "model", "context_id"))
        and actor["kind"] in {"AI", "HUMAN", "SYNTHETIC"},
        "visible reviewer identity/model/context/kind absent",
    )
    if actor["kind"] == "HUMAN":
        _need(
            "synthetic" not in " ".join(str(v) for v in actor.values()).casefold(),
            "synthetic test actor cannot be represented as a human reviewer",
        )
    if actor["kind"] == "SYNTHETIC":
        _need(
            m["is_synthetic"] is True,
            "synthetic visual evidence cannot certify a nonsynthetic product",
        )
    _auth(p, actor["id"])
    viewed = RE.timestamp(p["completed_at"])
    _need(
        viewed <= RE.timestamp(report.get("completed_at")),
        "FORMAT report predates its visual metadata review",
    )
    _need(
        type(p["completion_page"]) is int and 1 <= p["completion_page"] <= count,
        "completion date page absent",
    )
    pages = p["sources_pages"]
    _need(
        isinstance(pages, list)
        and pages
        and all(type(n) is int and 1 <= n <= count for n in pages)
        and pages == sorted(set(pages)),
        "complete bibliography page inventory absent",
    )
    needed = {p["completion_page"], *pages}
    if dates["revision_date"] is not None:
        _need(
            type(p["revision_page"]) is int and 1 <= p["revision_page"] <= count,
            "revision date page absent",
        )
        needed.add(p["revision_page"])
    else:
        _need(
            p["revision_page"] is None,
            "initial completion claims an unrelated revision-page check",
        )
    renders = _records(p["rendered_pages"])
    found = []
    for r in renders:
        _record(r, {"page", "artifact"}, {"rendered_at", "available_at"})
        _need(
            ("rendered_at" in r) != ("available_at" in r),
            "render evidence needs exactly one actual render time or recorded availability observation",
        )
        _need(
            type(r["page"]) is int and 1 <= r["page"] <= count,
            "viewed render page invalid",
        )
        _need(
            RE.timestamp(r.get("rendered_at", r.get("available_at"))) <= viewed,
            "page was rendered/observed available after the claimed actual view",
        )
        _png(_read(root, r["artifact"]))
        found.append(r["page"])
    _need(
        len(found) == len(set(found)) and set(found) == needed,
        "visible completion/bibliography pages lack exact render artifacts",
    )


def _log(root: Any, ref: Any, subject: dict, dates: dict, m: dict, pdf: dict) -> None:
    r = RE.report(root, ref, "TRANSLATION_LOG_READBACK", subject)
    doc = _read(root, r.get("artifact"), obj=True)
    _need(
        doc.get("documentId") == r.get("log_document_id")
        and doc.get("revisionId") == r.get("log_document_revision_id")
        and RE.nonempty(r.get("log_document_id"))
        and RE.nonempty(r.get("log_document_revision_id")),
        "actual LOG identity/revision differs",
    )
    p = _record(
        r.get("publication_metadata"),
        {
            "tab_id",
            "entry_paragraph_starts",
            "completion_date",
            "revision_date",
            "completion_label",
            "revision_label",
        },
    )
    rows = _body(doc, p["tab_id"])
    starts = p["entry_paragraph_starts"]
    _need(
        isinstance(starts, list)
        and starts
        and all(type(n) is int for n in starts)
        and len(set(starts)) == len(starts),
        "exact full LOG entry paragraph inventory absent",
    )
    selected = [_row(rows, n) for n in starts]
    positions = [rows.index(row) for row in selected]
    _need(
        positions == list(range(positions[0], positions[0] + len(positions))),
        "LOG entry paragraph selection is discontinuous",
    )
    entry = _text(" ".join(row["text"] for row in selected))
    _need(
        entry == _text(r.get("entry_text")) and RE.nonempty(r.get("entry_id")),
        "metadata dates are not in the actual complete LOG entry",
    )
    _need(
        sum(r["entry_id"] in row.get("text", "") for row in rows) == 1,
        "LOG event identity is absent or duplicated",
    )
    for token in (
        r["entry_id"],
        subject["subject_id"],
        subject["revision_id"],
        m["native"]["document_id"],
        m["native"]["revision_id"],
        pdf.get("permanent_uri"),
    ):
        _need(
            _string(token, "LOG publication binding") in entry,
            "LOG entry is bound to another publication artifact",
        )
    _need(
        RE.timestamp(r.get("written_at")) >= RE.timestamp(pdf.get("completed_at"))
        and RE.timestamp(r["completed_at"]) >= RE.timestamp(r["written_at"]),
        "LOG date/readback predates current completed PDF FORMAT",
    )
    for kind, labels in [
        ("completion", COMPLETION_LABELS),
        ("revision", REVISION_LABELS),
    ]:
        key = kind + "_date"
        label = p[kind + "_label"]
        _need(
            p[key] == dates[key],
            "LOG recorded " + key + " differs from original/revision evidence",
        )
        if dates[key] is None:
            _need(label is None, "initial LOG entry claims a revision date")
            continue
        _need(label in labels, "LOG field is not labelled as completion/revision")
        for row in selected:
            _current_date_fields(row, dates[key], revision=kind == "revision")
        matches = re.findall(re.escape(label) + r"\s*(\d{4}-\d{2}-\d{2})(?!\d)", entry)
        _need(
            matches == [dates[key]],
            "proper LOG completion/revision field is missing, duplicated or another day",
        )


def validate(
    root: Any,
    manifest_ref: Any,
    *,
    subject: Any,
    source_case: Any,
    native_ref: Any,
    pdf_report: Any,
    log_ref: Any,
    requested_channels: Any = (),
) -> dict:
    """Check existing evidence without edits, source reads, network or authority.

    requested_channels is the independent task scope, not a default inferred
    from this manifest. pdf_report is the already verified decoded FORMAT_PDF
    report; log_ref is the exact external TRANSLATION_LOG_READBACK artifact ref.
    All positive results remain structural evidence, never publication approval.
    """
    result: dict = {
        "status": "HOLD",
        "ready_for_publication": False,
        "structural_only": True,
        "standard_activated": False,
        "checks": [],
        "errors": [],
        "rule_ids": ["SF-RULE-OPS-004", "SF-RULE-PUB-001", "SF-RULE-PUB-002"],
    }
    stage = "MANIFEST"
    try:
        _need(
            isinstance(subject, dict)
            and isinstance(source_case, dict)
            and isinstance(pdf_report, dict),
            "independently verified subject/source case/PDF report absent",
        )
        units = RE.scope(subject.get("scope"))
        bundle = _read(root, subject.get("content"), obj=True)
        m = _read(root, manifest_ref, obj=True)
        _record(
            m,
            {
                "schema",
                "is_synthetic",
                "subject_id",
                "revision_id",
                "scope",
                "components",
                "native",
                "dates",
                "bibliography",
                "channels",
            },
        )
        _need(
            m["schema"] == "suttaflow-publication-metadata-v2"
            and type(m["is_synthetic"]) is bool,
            "publication metadata schema/synthetic flag absent",
        )
        _need(
            bundle.get("schema") == "suttaflow-publication-bundle-v2"
            and bundle.get("publication_metadata") == manifest_ref,
            "metadata is not the manifest pinned by the whole publication bundle",
        )
        _need(
            all(
                m[k] == subject.get(k) == bundle.get(k)
                for k in ("subject_id", "revision_id", "scope")
            )
            and m["scope"] == units,
            "metadata manifest identity/revision/scope differs from the whole task",
        )
        components = _record(m["components"], {"core", "apparatus", "interpretation"})
        for key, ref in components.items():
            _need(
                ref == bundle.get(key),
                "metadata component pin differs from actual bundle " + key,
            )
            _read(root, ref)
        n = _record(m["native"], {"document_id", "revision_id", "tab_id"})
        _need(
            RE.nonempty(n["document_id"]) and RE.nonempty(n["revision_id"]),
            "native identity/revision absent",
        )
        _record(m["bibliography"], {"heading_start", "entries"})
        result["is_synthetic"] = m["is_synthetic"]
        result["checks"].append(stage)
        stage = "NATIVE"
        doc = _read(root, native_ref, obj=True)
        _need(
            doc.get("documentId") == n["document_id"]
            and doc.get("revisionId") == n["revision_id"],
            "actual native document identity/revision differs from manifest",
        )
        rows = _body(doc, n["tab_id"])
        result["checks"].append(stage)
        stage = "DATES"
        dates = _dates(root, m, subject, doc, rows)
        result["dates"] = dates
        result["checks"].append(stage)
        stage = "BIBLIOGRAPHY"
        metadata = _record(
            pdf_report.get("publication_metadata"),
            {"source_evidence_index", "visual_review"},
        )
        index = _read(root, metadata["source_evidence_index"], obj=True)
        expected, disclosure = _expected_bibliography(
            root, m, source_case, index, subject
        )
        blocks = _native_bibliography(
            rows, m["bibliography"]["heading_start"], expected, disclosure
        )
        result["source_ids"] = [r["source_id"] for r in expected]
        result["checks"].append(stage)
        stage = "CHANNELS"
        _channels(root, m, requested_channels, expected, disclosure)
        result["checks"].append(stage)
        stage = "PDF"
        _pdf(
            root,
            pdf_report,
            subject,
            native_ref,
            m,
            dates,
            blocks,
            result["source_ids"],
        )
        result["checks"].append(stage)
        stage = "LOG"
        _log(root, log_ref, subject, dates, m, pdf_report)
        result["checks"].append(stage)
        result["status"] = READY
    except (
        RE.EvidenceError,
        KeyError,
        TypeError,
        ValueError,
        UnicodeError,
        OSError,
        IndexError,
        ZoneInfoNotFoundError,
        struct.error,
    ) as exc:
        result["errors"].append(
            {"code": "METADATA_" + stage + "_INVALID", "message": str(exc)}
        )
    return result
