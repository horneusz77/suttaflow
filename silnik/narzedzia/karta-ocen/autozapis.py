"""Loopback-only card with an atomic, source-pinned JSON autosave. Standard library only."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import tempfile
from threading import Thread
from urllib.error import URLError
from urllib.request import Request, urlopen
import webbrowser

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_model(card):
    return json.loads(re.search(r'<script type="application/json" id="sf-card-model">(.*?)</script>', card.read_text(encoding="utf-8"), re.S)[1])


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".save-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


class Conflict(ValueError):
    pass


@contextmanager
def file_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        if not stream.seek(0, os.SEEK_END):
            stream.write(b'\0'); stream.flush()
        stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise Conflict('Ten JSON jest już używany przez inny serwer lub zapis. Zachowaj szkic i użyj istniejącej sesji.') from error
        # Keep the lock file: unlinking it could let a new inode bypass a current lock.
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


class Store:
    def __init__(self, model, root=REPO):
        self.model, self.root = model, root.resolve()
        self.path = (self.root / model["decision_path"]).resolve()
        source = (self.root / model["source_path"]).resolve()
        if (not self.path.is_relative_to(self.root) or not source.is_relative_to(self.root)
                or self.path.parent.name != "karta-ocen" or self.path.suffix != ".json"
                or source.parent.parent != self.path.parent.parent):
            raise ValueError("JSON musi być w karta-ocen/ tego samego zadania co przekład.")
        self.backup = self.path.with_suffix(".przed-autozapisem.json")
        self.previous = self.path.with_suffix(".poprzedni.json")

    def check_source(self):
        if sha((self.root / self.model["source_path"]).read_bytes()) != self.model["source_sha256"]:
            raise ValueError("Źródło zmieniło się. Karta wymaga ponownego powiązania.")

    def validate(self, draft):
        m = self.model
        if (not isinstance(draft, dict) or draft.get("schema") != "suttaflow-choice-draft-v1"
                or any(draft.get(k) != m[k] for k in ("card_id", "source_sha256"))
                or not isinstance(draft.get("choices"), dict) or not isinstance(draft.get("saved_at"), str)):
            raise ValueError("Szkic nie pasuje do karty i źródła.")
        datetime.fromisoformat(draft["saved_at"].replace("Z", "+00:00"))
        issues = {i["id"]: i for i in m["issues"]}
        if not draft["choices"].keys() <= issues.keys():
            raise ValueError("Nieznane ID uwagi.")
        for key, c in draft["choices"].items():
            if (not isinstance(c, dict) or c.get("option") not in ["", "CUSTOM", "KEEP", "DEFER", *[o["id"] for o in issues[key]["options"]]]
                    or any(not isinstance(c.get(k), str) or len(c[k]) > limit for k, limit in [("text", 1800), ("note", 1800), ("comment", 1200)])
                    or c.get("preview_scope", "fragment") not in ("fragment", "paragraph")):
                raise ValueError("Niepoprawny wybór lub zbyt długie pole.")

    def export(self, draft, created_at):
        m = self.model
        result = {k: m[k] for k in ("card_id", "subject", "revision", "source_path", "source_sha256", "audit_path", "audit_sha256", "standard_version", "standard_sha256", "scope")}
        result.update(schema="suttaflow-choice-export-v1", status="DRAFT_FOR_OWNER_REVIEW", created_at=created_at,
                      saved_at=draft["saved_at"], approval_evidence=None, issues=[], draft=draft)
        for i in m["issues"]:
            c = draft["choices"].get(i["id"], {})
            option = c.get("option", "")
            selected = next((o for o in i["options"] if o["id"] == option), {})
            item = dict(id=i["id"], locus=i["locus"], original=i["quote"], option=option or "UNSELECTED",
                        status="UNSELECTED" if not option else "NEEDS_CLARIFICATION" if option == "DEFER" else "DRAFT_CHOICE",
                        wording=c["text"].strip() if option == "CUSTOM" else selected.get("text", i["quote"] if option == "KEEP" else ""),
                        note=c["note"].strip() if option == "CUSTOM" else selected.get("note", ""), comment=c.get("comment", "").strip(), implemented=False)
            if option == "CUSTOM":
                item["preview_scope"] = c.get("preview_scope", "fragment")
            result["issues"].append(item)
        return result

    def load(self):
        self.check_source()
        if not self.path.exists():
            return dict(schema="suttaflow-choice-draft-v1", card_id=self.model["card_id"], source_sha256=self.model["source_sha256"],
                        saved_at="1970-01-01T00:00:00Z", choices={}), None
        raw = self.path.read_bytes()
        data = json.loads(raw)
        if (not isinstance(data, dict) or data.get("schema") != "suttaflow-choice-export-v1" or data.get("status") != "DRAFT_FOR_OWNER_REVIEW"
                or data.get("approval_evidence") is not None
                or any(data.get(k) != self.model[k] for k in ("card_id", "source_sha256", "source_path", "audit_sha256", "standard_sha256"))
                or [i["id"] for i in data["issues"]] != [i["id"] for i in self.model["issues"]]
                or any(i.get("implemented") is not False for i in data["issues"])):
            raise ValueError("Plik nie jest zgodnym szkicem tej karty; odmowa nadpisania.")
        draft = data.get("draft") or dict(schema="suttaflow-choice-draft-v1", card_id=data["card_id"], source_sha256=data["source_sha256"],
            saved_at=data["created_at"], choices={i["id"]: dict(option="" if i["option"] == "UNSELECTED" else i["option"],
            text=i["wording"] if i["option"] == "CUSTOM" else "", note=i["note"] if i["option"] == "CUSTOM" else "", comment=i["comment"],
            **({"preview_scope": i["preview_scope"]} if "preview_scope" in i else {})) for i in data["issues"]})
        self.validate(draft)
        if self.export(draft, data["created_at"])["issues"] != data["issues"]:
            raise ValueError("Warianty w JSON różnią się od karty; odmowa nadpisania.")
        return draft, sha(raw)

    def save(self, draft, expected):
        with file_lock(self.path.with_suffix('.write.lock')):
            return self._save(draft, expected)

    def _save(self, draft, expected):
        self.validate(draft)
        _, actual = self.load()
        if actual != expected:
            raise Conflict("JSON zmienił się w innej karcie lub poza formularzem. Zachowaj szkic i otwórz kartę ponownie.")
        old = self.path.read_bytes() if self.path.exists() else None
        created = json.loads(old)["created_at"] if old else datetime.now(timezone.utc).isoformat()
        data = (json.dumps(self.export(draft, created), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if old is not None:
            if not self.backup.exists():
                atomic(self.backup, old)
            atomic(self.previous, old)
        # Catch an external edit during backup preparation as well.
        if (sha(self.path.read_bytes()) if self.path.exists() else None) != expected:
            raise Conflict("JSON zmienił się podczas zapisu; zachowano nowszy plik.")
        atomic(self.path, data)
        return sha(data)


def make_server(card, root=REPO, port=0):
    store = Store(read_model(card), root)
    store.load()  # Fail before serving, never start with a blank replacement for a bad file.
    fragment = card.read_text(encoding="utf-8")
    card_sha256 = sha(card.read_bytes())
    token = "/" + secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, data, kind="application/json"):
            body = data.encode("utf-8") if isinstance(data, str) else json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; form-action 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def allowed(self):
            return self.headers.get("Host") == self.server.origin.removeprefix("http://")

        def do_GET(self):
            if not self.allowed():
                return self.reply(403, {"error": "Host odmówiony"})
            try:
                if self.path == token + "/status":
                    return self.reply(200, {"card_id": store.model["card_id"], "source_sha256": store.model["source_sha256"], "card_sha256": card_sha256, "pid": os.getpid()})
                if self.path != token + "/":
                    return self.reply(404, {"error": "Brak zasobu"})
                draft, version = store.load()
                boot = json.dumps(dict(initial=draft, version=version, endpoint=token + "/save"), ensure_ascii=False).replace("<", "\\u003c")
                bridge = (HERE / "dysk.js").read_text(encoding="utf-8")
                page = '<!doctype html><html lang="pl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Karta ocen · SuttaFlow</title><body>'
                page += '<script>window.sfDiskBoot=' + boot + ';</script><script>' + bridge + '</script>'
                page += fragment + '</body></html>'
                return self.reply(200, page, "text/html")
            except (ValueError, OSError, KeyError, TypeError) as error:
                return self.reply(409, {"error": str(error)})

        def do_POST(self):
            if (not self.allowed() or self.path not in (token + "/save", token + "/stop") or self.headers.get("Origin") != self.server.origin
                    or self.headers.get("Content-Type") != "application/json"):
                return self.reply(403, {"error": "Zapis tylko z lokalnej karty"})
            if self.path == token + "/stop":
                self.reply(200, {"stopped": True})
                Thread(target=self.server.shutdown, daemon=True).start()
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 150000:
                    return self.reply(413, {"error": "Zbyt duży zapis"})
                request = json.loads(self.rfile.read(size))
                version = store.save(request["draft"], request["version"])
                return self.reply(200, {"version": version})
            except Conflict as error:
                return self.reply(409, {"error": str(error)})
            except (ValueError, OSError, KeyError, TypeError) as error:
                return self.reply(400, {"error": str(error)})

    class LocalServer(HTTPServer):
        def __init__(self):
            self.lease = file_lock(store.path.with_suffix('.server.lock'))
            self.lease.__enter__()
            try:
                super().__init__(("127.0.0.1", port), Handler)
            except BaseException:
                self.lease.__exit__(None, None, None)
                raise

        def server_close(self):
            try:
                super().server_close()
            finally:
                self.lease.__exit__(None, None, None)

    server = LocalServer()
    server.timeout = 10
    server.origin = "http://127.0.0.1:" + str(server.server_port)
    server.card_url = server.origin + token + "/"
    server.store = store
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card", type=Path, default=HERE / "karta.html")
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--stop", action="store_true", help="Zatrzymaj wyłącznie serwer tej karty.")
    args = parser.parse_args()
    store = Store(read_model(args.card))
    session = store.path.parent / ".karta-serwer.json"
    if (args.open or args.stop) and session.exists():
        try:
            prior = json.loads(session.read_bytes())
            url = prior["url"]
            if not re.fullmatch(r"http://127\.0\.0\.1:\d+/[A-Za-z0-9_-]+/", url):
                raise ValueError("Niepoprawny adres sesji")
            with urlopen(url + "status", timeout=2) as response:
                status = json.load(response)
            if args.stop and status["card_id"] == store.model["card_id"]:
                origin = url.rsplit("/", 2)[0]
                request = Request(url + "stop", data=b"{}", headers={"Origin": origin, "Content-Type": "application/json"})
                with urlopen(request, timeout=3):
                    return
            if (status["card_id"] == store.model["card_id"] and status["source_sha256"] == store.model["source_sha256"]
                    and status.get("card_sha256") == sha(args.card.read_bytes())):
                webbrowser.open(url)
                return
        except (OSError, ValueError, URLError, KeyError):
            pass
    if args.stop:
        return
    server = make_server(args.card)
    atomic(session, json.dumps(dict(url=server.card_url, pid=os.getpid())).encode())
    if args.open:
        webbrowser.open(server.card_url)
    if __import__("sys").stdout:
        print(server.card_url, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if session.exists() and json.loads(session.read_bytes()).get("pid") == os.getpid():
            session.unlink()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        if __import__("sys").stderr is None:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, str(error), "SuttaFlow — karta nie została otwarta", 16)
        else:
            raise
