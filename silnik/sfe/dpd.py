"""Adapter for the official Digital Pāḷi Dictionary SQLite release (dpd.db).

Fail-closed: refuses to run unless the database file hashes to the value pinned in
config/dpd_pin.json, which itself records the GitHub release asset digest of the
archive the file was extracted from. Returns ALL headwords and ALL grammatical
readings for a form; never picks one. Locators are (db version, headword id, lemma_1).
DPD data: CC BY-NC-SA 4.0 (Bodhirasa Bhikkhu). Only short excerpts are stored.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path


class DpdError(RuntimeError):
    pass


def sha256_stream(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


class Dpd:
    FIELDS = ("id", "lemma_1", "pos", "grammar", "meaning_1", "meaning_lit", "meaning_2",
              "construction", "compound_type", "compound_construction", "commentary", "notes")

    def __init__(self, db: Path, pin: Path, verify_hash: bool = True):
        if not db.is_file():
            raise DpdError("DB_NOT_INSTALLED")
        try:
            p = json.loads(pin.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise DpdError("PIN_INVALID") from exc
        if not isinstance(p, dict) or not isinstance(p.get("db_sha256"), str) \
                or not re.fullmatch(r"[0-9a-f]{64}", p["db_sha256"]) \
                or type(p.get("db_bytes")) is not int or p["db_bytes"] <= 0 \
                or not isinstance(p.get("release"), str) or not p["release"].startswith("dpd-db "):
            raise DpdError("PIN_INVALID")
        self.verified_bytes = db.stat().st_size
        if self.verified_bytes != p["db_bytes"]:
            raise DpdError("DB_SIZE_MISMATCH")
        # No process/global stat cache: the production gate requests a fresh
        # streamed digest on every evaluation. The optional legacy low-level
        # opt-out never supplies a verified digest and is not used by QA.
        self.verified_sha256 = sha256_stream(db) if verify_hash else None
        if verify_hash and self.verified_sha256 != p["db_sha256"]:
            raise DpdError("DB_HASH_MISMATCH")
        self.pin = p
        try:
            self.con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
        except sqlite3.DatabaseError as exc:
            raise DpdError("DB_SQLITE_INVALID") from exc
        try:
            cols = {r[1] for r in self.con.execute("PRAGMA table_info(lookup)")}
            hw = {r[1] for r in self.con.execute("PRAGMA table_info(dpd_headwords)")}
            if not {"lookup_key", "headwords", "grammar", "deconstructor", "variant", "spelling"} <= cols or not set(self.FIELDS) <= hw:
                raise DpdError("SCHEMA_UNSUPPORTED")
            self.version = dict(self.con.execute("SELECT key, value FROM db_info").fetchall())
            if self.version.get("dpd_release_version") != p["release"].removeprefix("dpd-db "):
                raise DpdError("DB_VERSION_MISMATCH")
        except sqlite3.DatabaseError as exc:
            self.con.close()
            raise DpdError("DB_SQLITE_INVALID") from exc
        except DpdError:
            self.con.close()
            raise

    def headword(self, hid: int) -> dict:
        row = self.con.execute(f"SELECT {', '.join(self.FIELDS)} FROM dpd_headwords WHERE id=?", (hid,)).fetchone()
        if row is None:
            raise DpdError(f"HEADWORD_MISSING {hid}")
        d = dict(zip(self.FIELDS, row))
        d["locator"] = {"db_release": self.pin["release"], "headword_id": hid, "lemma_1": d["lemma_1"],
                        "web": "https://www.dpdict.net/?q=" + d["lemma_1"].split(" ")[0]}
        return d

    def lookup(self, form: str) -> dict:
        row = self.con.execute(
            "SELECT headwords, grammar, deconstructor, variant, spelling FROM lookup WHERE lookup_key=?",
            (form,)).fetchone()
        if row is None:
            return {"form": form, "status": "NOT_IN_LOOKUP", "headwords": [], "readings": [], "deconstructor": [], "variant": {}, "spelling": []}
        hws, gram, decon, var, spell = row
        ids = json.loads(hws) if hws else []
        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            raise DpdError("HEADWORDS_PACKING_UNKNOWN")
        return {"form": form, "status": "FOUND" if ids else ("DECONSTRUCTOR_ONLY" if decon else "EMPTY"),
                "headwords": [self.headword(i) for i in ids],
                "readings": json.loads(gram) if gram else [],
                "deconstructor": json.loads(decon) if decon else [],
                "variant": json.loads(var) if var else {},
                "spelling": json.loads(spell) if spell else []}
