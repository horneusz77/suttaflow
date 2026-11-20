"""Raw-byte importer for SuttaFlow sources.

Stores the exact bytes served, HTTP headers, fetch time and SHA-256. For GitHub
sources it additionally records the git blob SHA-1 reported by the GitHub API for the
pinned commit and checks that the downloaded bytes hash to that blob. That check is an
anchor outside our control: anyone can repeat it against GitHub.

Web pages without such an anchor are recorded as ANCHOR_NONE_SELF_CAPTURE and may be
cross-checked against the Internet Archive (read-only availability query).
Nothing is normalised here; normalisation happens later, reversibly, on copies.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.error
import urllib.request
import urllib.parse
from pathlib import Path

UA = "SuttaFlow-RC-importer/1.0 (+evidence capture; contact via project owner)"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def fetch(url: str) -> tuple[bytes, dict, int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read(), dict(r.headers.items()), r.status, r.geturl()


def github_anchor(src: dict) -> dict:
    api = (f"https://api.github.com/repos/{src['owner']}/{src['repo']}/contents/"
           f"{src['path']}?ref={src['ref']}")
    meta = json.loads(fetch(api)[0])
    return {"api_url": api, "git_blob_sha1": meta["sha"], "size": meta["size"],
            "raw_url": f"https://raw.githubusercontent.com/{src['owner']}/{src['repo']}/{src['ref']}/{src['path']}"}


def wayback(url: str) -> dict:
    try:
        q = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
        d = json.loads(fetch(q)[0])
        snap = d.get("archived_snapshots", {}).get("closest")
        return {"status": "FOUND", "snapshot": snap} if snap else {"status": "NONE"}
    except Exception as e:  # recorded, never hidden
        return {"status": "QUERY_FAILED", "error": repr(e)}


def capture(src: dict, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    rec = {"id": src["id"], "role": src["role"], "edition": src["edition"],
           "carrier": src["carrier"], "fetched_at_utc": now, "redistribute": src.get("redistribute", False)}
    try:
        if src["kind"] == "github":
            anc = github_anchor(src)
            data, headers, status, final = fetch(anc["raw_url"])
            blob = git_blob_sha1(data)
            rec.update(url=anc["raw_url"], anchor={"type": "GITHUB_GIT_BLOB", **anc,
                       "blob_matches": blob == anc["git_blob_sha1"], "computed_blob_sha1": blob})
        else:
            data, headers, status, final = fetch(src["url"])
            rec.update(url=src["url"], anchor={"type": "ANCHOR_NONE_SELF_CAPTURE",
                                               "wayback": wayback(src["url"])})
        ext = Path(rec["url"].split("?")[0]).suffix or ".bin"
        raw = out / f"{src['id']}{ext}"
        raw.write_bytes(data)
        (out / f"{src['id']}.headers.json").write_text(json.dumps(headers, indent=1), encoding="utf-8")
        rec.update(status="CAPTURED", http_status=status, final_url=final, file=raw.name,
                   bytes=len(data), sha256=sha256_file(raw),
                   content_type=headers.get("Content-Type"), last_modified=headers.get("Last-Modified"),
                   etag=headers.get("ETag"), server_date=headers.get("Date"))
        if src["kind"] == "github" and not rec["anchor"]["blob_matches"]:
            rec["status"] = "ANCHOR_MISMATCH"
    except (urllib.error.URLError, KeyError, ValueError) as e:
        rec.update(status="FETCH_FAILED", error=repr(e))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    cfg = json.loads(a.config.read_text(encoding="utf-8"))
    recs = [capture(s, a.out) for s in cfg["sources"] if not a.only or s["id"] in a.only]
    log = a.out / "capture_log.json"
    old = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    log.write_text(json.dumps(old + recs, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in recs:
        print(r["id"], r["status"], r.get("bytes"), r.get("sha256", "")[:16], r.get("anchor", {}).get("type"))
    return 0 if all(r["status"] == "CAPTURED" for r in recs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
