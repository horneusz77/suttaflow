"""Disk safety checks; all writes stay inside an isolated task fixture."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("autozapis", HERE / "autozapis.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class AutosaveTest(unittest.TestCase):
    def setUp(self):
        (HERE.parents[1] / "build/tmp").mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix=".test-disk-", dir=HERE.parents[1] / "build/tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        model = app.read_model(HERE / "karta.html")
        repo = HERE.parents[1]
        source = repo / model["source_path"]
        (self.root / "wyniki").mkdir()
        (self.root / "wyniki/MN53-R9.md").write_bytes(source.read_bytes())
        self.original = (HERE / "test-fixture.json").read_bytes()
        model["source_path"] = "wyniki/MN53-R9.md"
        model["decision_path"] = "karta-ocen/wybory.json"
        self.store = app.Store(model, self.root)
        self.store.path.parent.mkdir()
        original = json.loads(self.original)
        original["source_path"] = model["source_path"]
        self.original = json.dumps(original, ensure_ascii=False).encode()
        self.store.path.write_bytes(self.original)

    def test_roundtrip_and_backups(self):
        draft, sha = self.store.load()
        self.assertEqual(len(draft["choices"]), 10)
        self.assertEqual(draft["choices"]["MN53-S07"]["option"], "B")
        self.assertIn("postać", draft["choices"]["MN53-S04"]["comment"])
        self.assertEqual(self.store.path.read_bytes(), self.original)  # Reading never rewrites.
        draft["choices"]["MN53-S01"].update(option="CUSTOM", text="  szkic  ", note="", preview_scope="paragraph")
        result = self.store.save(draft, sha)
        restored, actual = self.store.load()
        self.assertEqual(restored, draft)
        self.assertEqual(actual, result)
        self.assertEqual(self.store.backup.read_bytes(), self.original)
        self.assertEqual(self.store.previous.read_bytes(), self.original)
        exported = json.loads(self.store.path.read_bytes())
        self.assertFalse(exported["issues"][0]["implemented"])
        self.assertIsNone(exported["approval_evidence"])
        self.assertEqual(exported["draft"]["choices"]["MN53-S01"]["text"], "  szkic  ")
        with self.assertRaises(app.Conflict):
            self.store.save(draft, sha)

    def test_invalid_and_stale_source_do_not_write(self):
        draft, sha = self.store.load()
        for key, value in [("source_sha256", "0" * 64), ("card_id", "foreign")]:
            bad = copy.deepcopy(draft)
            bad[key] = value
            with self.assertRaises(ValueError):
                self.store.save(bad, sha)
        bad = copy.deepcopy(draft)
        bad["choices"]["MN53-S01"]["comment"] = "x" * 1201
        with self.assertRaises(ValueError):
            self.store.save(bad, sha)
        (self.root / self.store.model["source_path"]).write_text("changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.save(draft, sha)
        self.assertEqual(self.store.path.read_bytes(), self.original)

    def test_incomplete_custom_and_empty_card(self):
        draft, sha = self.store.load()
        draft["choices"]["MN53-S01"].update(option="CUSTOM", text="")
        self.store.save(draft, sha)
        self.assertEqual(self.store.load()[0], draft)
        self.store.path.unlink()
        empty, sha = self.store.load()
        self.assertEqual(empty["choices"], {})
        self.assertIsNone(sha)
        self.store.save(empty, sha)
        self.assertEqual(len(json.loads(self.store.path.read_bytes())["issues"]), 10)

    def test_damaged_or_mismatched_file_is_never_replaced(self):
        draft, sha = self.store.load()
        for damaged in (b"not json", b"[]"):
            self.store.path.write_bytes(damaged)
            with self.assertRaises(ValueError):
                self.store.save(draft, sha)
            self.assertEqual(self.store.path.read_bytes(), damaged)
        data = json.loads(self.original)
        data["issues"][0]["wording"] = "Changed option outside this card"
        raw = json.dumps(data).encode()
        self.store.path.write_bytes(raw)
        with self.assertRaises(ValueError):
            self.store.load()
        self.assertEqual(self.store.path.read_bytes(), raw)

    def test_two_processes_cannot_both_save_the_same_version(self):
        script = '''
import importlib.util,json,sys,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('autozapis',sys.argv[1]); app=importlib.util.module_from_spec(spec); spec.loader.exec_module(app)
store=app.Store(json.loads(Path(sys.argv[3]).read_text(encoding='utf-8')),Path(sys.argv[2])); draft,version=store.load()
draft['choices']['MN53-S01']['comment']=sys.argv[4]
atomic=app.atomic
def delayed(path,data):
    if path==store.path: time.sleep(.3)
    atomic(path,data)
app.atomic=delayed
print('READY',flush=True); sys.stdin.readline()
try: store.save(draft,version); print('SAVED',flush=True)
except app.Conflict: print('CONFLICT',flush=True)
'''
        model_path = self.root/'model.json'
        model_path.write_text(json.dumps(self.store.model), encoding='utf-8')
        writers = [subprocess.Popen([sys.executable, '-u', '-c', script, str(HERE/'autozapis.py'),
                   str(self.root), str(model_path), label], stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for label in ('A', 'B')]
        try:
            for writer in writers:
                self.assertEqual(writer.stdout.readline().strip(), 'READY')
            for writer in writers:
                writer.stdin.write('GO\n'); writer.stdin.flush()
            results = [writer.communicate(timeout=10) for writer in writers]
            self.assertEqual(sorted(out.strip() for out, _ in results), ['CONFLICT', 'SAVED'], results)
            self.assertTrue(all(writer.returncode == 0 for writer in writers), results)
            self.assertIn(self.store.load()[0]['choices']['MN53-S01']['comment'], ('A', 'B'))
            self.assertEqual(self.store.backup.read_bytes(), self.original)
        finally:
            for writer in writers:
                if writer.poll() is None:
                    writer.kill(); writer.communicate()

    def test_second_server_is_refused_and_close_releases_lease(self):
        card = self.root/'card.html'
        card.write_text('<script type="application/json" id="sf-card-model">' + json.dumps(self.store.model) + '</script>', encoding='utf-8')
        server = app.make_server(card, self.root)
        try:
            with self.assertRaises(app.Conflict):
                app.make_server(card, self.root)
        finally:
            server.server_close()
        reopened = app.make_server(card, self.root)
        reopened.server_close()


if __name__ == "__main__":
    unittest.main()
