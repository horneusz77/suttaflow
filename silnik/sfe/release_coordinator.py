"""A fail-closed Git/Docs migration coordinator; it issues no release consent.

The authoritative ref and its access policy are supplied by a trusted runner.
GitHub REST has no expected-old-SHA parameter. Linear, single-parent commits and
non-forced ref updates provide sibling exclusion; rewinds/deletion/other writers
must be prevented outside this module. Google Docs is a separate transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import copy
import hashlib
import json
import re
from functools import wraps
from typing import Callable, Mapping, Protocol
from urllib.parse import quote


SCHEMA = "suttaflow-release-coordinator-v1"
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
DOC_ID = re.compile(r"[A-Za-z0-9_-]{16,160}\Z")
ACTION_STATES = {"PREPARED", "DISPATCHED", "ACKNOWLEDGED", "APPLIED", "NOT_APPLIED", "UNKNOWN"}
UNRESOLVED = {"PREPARED", "DISPATCHED", "ACKNOWLEDGED", "UNKNOWN"}
PROJECTION_STAGES = {"UNAPPROVED", "DEPLOYMENT_IN_PROGRESS", "PARTIAL_DEPLOYMENT",
                     "ACTIVE_SYNCHRONIZED", "RELEASE_BLOCKED", "ROLLBACK_IN_PROGRESS",
                     "ROLLBACK_VERIFIED"}


class Hold(RuntimeError):
    """No permission to continue. An attempted commit is evidence, not success."""

    def __init__(self, reason: str, *, attempted_head: str | None = None):
        super().__init__(reason)
        self.reason = reason
        self.attempted_head = attempted_head


class Rejected(RuntimeError):
    """Transport-confirmed rejection with no effect, e.g. Docs HTTP 400."""

    def __init__(self, reason: str, raw: bytes):
        super().__init__(reason)
        self.raw = raw


def _fail_closed(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Hold:
            raise
        except Exception as exc:
            raise Hold("input/transport unavailable or malformed: " + str(exc)) from exc
    return guarded


def _require(condition, reason):
    if not condition:
        raise Hold(reason)


def _keys(obj, expected, label):
    _require(isinstance(obj, dict) and set(obj) == set(expected), label + ": fields differ")


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def json_bytes(value) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                           allow_nan=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise Hold("non-canonical JSON value") from exc


def parse_json(raw: bytes):
    _require(isinstance(raw, bytes), "expected raw bytes")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(Hold("non-finite JSON")))
    except (ValueError, UnicodeError) as exc:
        raise Hold("invalid JSON bytes") from exc
    _require(isinstance(value, dict), "JSON object required")
    return value


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _instant(value: str) -> datetime:
    _require(isinstance(value, str), "timestamp is not a string")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Hold("invalid timestamp") from exc
    offset = dt.utcoffset()
    _require(dt.tzinfo is not None and offset is not None and offset.total_seconds() == 0,
             "timestamp must have an explicit UTC offset")
    return dt


def _stamp(dt: datetime) -> str:
    _require(isinstance(dt, datetime) and dt.tzinfo is not None, "trusted clock unavailable")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _id(value, label="identifier"):
    _require(isinstance(value, str) and IDENTIFIER.fullmatch(value), "invalid " + label)
    return value


def _sha(value, pattern=SHA256):
    _require(isinstance(value, str) and pattern.fullmatch(value), "invalid SHA")
    return value


def native_state(raw: bytes, document_id: str) -> tuple[dict, dict]:
    """Complete GET only: all tabs, no field mask; ignore only top-level revision."""
    obj = parse_json(raw)
    _require(obj.get("documentId") == document_id, "foreign document response")
    _require(isinstance(obj.get("revisionId"), str) and obj["revisionId"], "revisionId absent")
    _require(isinstance(obj.get("tabs"), list) and obj["tabs"], "full includeTabsContent GET required")
    projection = copy.deepcopy(obj)
    del projection["revisionId"]
    return obj, {"revision_id": obj["revisionId"], "native_sha256": digest(json_bytes(projection))}


def _ack_revision(ack, document_id):
    _require(ack.get("documentId") == document_id, "ack document identity differs")
    control = ack.get("writeControl")
    _require(isinstance(control, dict) and "requiredRevisionId" in control and
             not set(control) - {"requiredRevisionId", "targetRevisionId", "writeMode"} and
             control.get("targetRevisionId") is None, "ack required revision absent or merge control present")
    _require(control.get("writeMode", "EDIT") in {"EDIT", "WRITE_MODE_UNSPECIFIED"}, "ack is not a normal edit")
    revision = control["requiredRevisionId"]
    _require(isinstance(revision, str) and revision, "ack revision absent")
    _require("revisionId" not in ack or ack["revisionId"] == revision, "ack top-level revision conflicts with write control")
    return revision


def _packed(raw: bytes) -> dict:
    _require(isinstance(raw, bytes), "raw evidence bytes required")
    return {"sha256": digest(raw), "bytes": len(raw), "base64": base64.b64encode(raw).decode("ascii")}


def _unpacked(value: dict) -> bytes:
    _keys(value, {"sha256", "bytes", "base64"}, "raw evidence")
    _sha(value["sha256"])
    _require(type(value["bytes"]) is int and value["bytes"] >= 0, "invalid evidence byte count")
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (ValueError, TypeError) as exc:
        raise Hold("invalid evidence encoding") from exc
    _require(len(raw) == value["bytes"] and digest(raw) == value["sha256"], "evidence bytes differ")
    return raw


@dataclass(frozen=True)
class Binding:
    repository: str
    branch: str
    anchor_head: str
    canonical_document_id: str
    scope_document_ids: tuple[str, ...]
    namespace: str = "release-control/v1"

    def __post_init__(self):
        _require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repository)), "invalid repository")
        _require(bool(re.fullmatch(r"[A-Za-z0-9_./-]+", self.branch)) and
                 not any(x in self.branch for x in ("..", "//", "@{")) and
                 not self.branch.startswith(("/", ".")) and not self.branch.endswith(("/", ".", ".lock")),
                 "invalid branch")
        _sha(self.anchor_head, SHA1)
        _require(isinstance(self.scope_document_ids, tuple) and self.scope_document_ids and
                 tuple(sorted(set(self.scope_document_ids))) == self.scope_document_ids, "scope must be a sorted unique tuple")
        _require(all(isinstance(x, str) and DOC_ID.fullmatch(x) for x in self.scope_document_ids), "canonical Doc IDs required; no URLs or titles")
        _require(self.canonical_document_id in self.scope_document_ids, "canonical document outside scope")
        _require(bool(re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", self.namespace)), "invalid namespace")

    @property
    def manifest_path(self):
        return self.namespace + "/manifest.json"

    def record(self):
        return {"repository": self.repository, "branch": self.branch, "anchor_head": self.anchor_head,
                "canonical_document_id": self.canonical_document_id,
                "scope_document_ids": list(self.scope_document_ids), "namespace": self.namespace}


@dataclass(frozen=True)
class Checkpoint:
    head: str
    generation: int


@dataclass(frozen=True)
class Snapshot:
    head: str
    parents: tuple[str, ...]
    tree_sha: str
    entries: Mapping[str, tuple[str, str]]  # regular-file path -> (mode, Git blob SHA)
    files: Mapping[str, bytes]  # full contents of this binding's namespace only


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    document_id: str
    plan_sha256: str
    requests: list[dict]
    postcondition: dict
    inverse_requests: list[dict] | dict | None  # None only for coordinator-built group compensation


class GitTransport(Protocol):
    def read_head(self) -> str: ...
    def snapshot(self, head: str) -> Snapshot: ...
    def create_commit(self, parent: str, changes: Mapping[str, bytes], message: str) -> str: ...
    def update_ref(self, expected: str, new: str) -> str: ...


class DocsTransport(Protocol):
    def get_document(self, document_id: str) -> bytes: ...
    def batch_update(self, document_id: str, body: dict) -> bytes: ...


def _projection(value):
    _keys(value, {"stage", "standard_active", "canonical_written_version", "activation_performed"}, "release projection")
    _require(value["stage"] in PROJECTION_STAGES, "unsupported release projection stage")
    _require(value["standard_active"] in {"UNVERIFIED", "1.13", "2.0"} and
             value["canonical_written_version"] in {"UNVERIFIED", "1.13", "2.0"}, "unsupported version projection")
    _require(type(value["activation_performed"]) is bool, "activation history must be boolean")
    _require(value["standard_active"] != "2.0" or value["activation_performed"], "operative 2.0 without activation history")
    _require(value["stage"] != "ACTIVE_SYNCHRONIZED" or
             (value["standard_active"] == "2.0" and value["canonical_written_version"] == "2.0"), "active projection differs")
    _require(value["stage"] not in {"ROLLBACK_IN_PROGRESS", "ROLLBACK_VERIFIED"} or value["standard_active"] == "1.13", "rollback lacks operative reversion")
    _require(value["stage"] != "ROLLBACK_VERIFIED" or value["canonical_written_version"] == "1.13", "rollback content unverified")


def _action(state, action_id):
    matches = [a for a in state["actions"] if a["action_id"] == action_id]
    _require(len(matches) == 1, "action absent or duplicated")
    return matches[0]


def _owned(state, actor, lease_id, now, *, allow_expired=False, allow_hold=False):
    lease = state["lease"]
    _require(lease is not None and lease["status"] == "ACTIVE", "no active lease")
    _require((lease["holder_id"], lease["lease_id"]) == (actor, lease_id), "wrong holder or lease")
    _require(allow_expired or now < _instant(lease["expires_at"]), "lease expired; automatic takeover forbidden")
    _require(allow_hold or state["hold"] is None, "execution is on HOLD")


def _unresolved(state):
    return [a for a in state["actions"] if a["status"] in UNRESOLVED]


def _stack(state):
    result = []
    for action in state["actions"]:
        if action["status"] != "APPLIED":
            continue
        if action["kind"] == "APPLY":
            result.append(action["action_id"])
        elif action["kind"] == "COMPENSATE":
            _require(result and result[-1] == action["compensates"], "compensation history order differs")
            result.pop()
        else:
            ids = action["compensates"]
            _require(action["kind"] == "COMPENSATE_GROUP" and isinstance(ids, list) and len(ids) >= 2 and
                     result[-len(ids):] == ids, "group compensation history order differs")
            del result[-len(ids):]
    return result


def _requests(value):
    _require(isinstance(value, list) and value and all(isinstance(x, dict) and len(x) == 1 for x in value), "nonempty Docs request array required")
    _require(not any("writeControl" in x or "documentId" in x for x in value), "write control belongs to the guarded envelope")
    json_bytes(value)


def _postcondition(value):
    _require(isinstance(value, dict), "postcondition absent")
    if value.get("kind") == "EXACT_NATIVE_STATE":
        _keys(value, {"kind", "sha256"}, "exact postcondition")
        _sha(value["sha256"])
    else:
        _keys(value, {"kind", "verifier_id", "parameters"}, "registered postcondition")
        _require(value["kind"] == "REGISTERED_NATIVE_TRANSFORM", "unknown postcondition kind")
        _id(value["verifier_id"], "verifier ID")
        _require(isinstance(value["parameters"], dict), "verifier parameters absent")


def _inverse_spec(value):
    if isinstance(value, list):
        _requests(value)
    elif isinstance(value, dict) and value.get("kind") == "REGISTERED_NATIVE_INVERSE":
        _keys(value, {"kind", "resolver_id", "parameters"}, "registered inverse")
        _id(value["resolver_id"], "inverse resolver ID")
        _require(isinstance(value["parameters"], dict), "inverse parameters absent")
    else:
        _keys(value, {"kind", "group_anchor_action_id"}, "group-only inverse")
        _require(value["kind"] == "GROUP_ONLY", "unknown inverse kind")
        _id(value["group_anchor_action_id"], "group anchor action ID")


def _deferred_inverse(action):
    value = action["inverse_requests"]
    return isinstance(value, dict) and value.get("kind") == "REGISTERED_NATIVE_INVERSE"


def _effective_inverse(action):
    value = action["inverse_requests"]
    if isinstance(value, dict):
        _require(_deferred_inverse(action) and action["status"] == "APPLIED" and
                 "resolved_inverse_requests" in action, "standalone inverse unavailable; verified group compensation required")
        value = action["resolved_inverse_requests"]
    _requests(value)
    return value


def _group_only_anchor(state, action):
    inverse = action["inverse_requests"]
    if not isinstance(inverse, dict) or inverse.get("kind") != "GROUP_ONLY":
        return
    stack = _stack(state)
    anchor = inverse["group_anchor_action_id"]
    _require(anchor in stack, "group-only inverse anchor is not an owned completed action")
    suffix = [_action(state, aid) for aid in stack[stack.index(anchor):]]
    _require(all(x["document_id"] == action["document_id"] for x in suffix), "group-only inverse crosses document scope")
    _effective_inverse(suffix[0])  # anchor must have a real bound standalone inverse
    _require(action["before"]["native_sha256"] == suffix[-1]["after_sha256"], "group-only action is not at the owned after-state")


def _group_actions(state, ids):
    _require(isinstance(ids, list) and len(ids) >= 2 and all(isinstance(x, str) for x in ids) and
             len(set(ids)) == len(ids), "group must contain at least two unique action IDs")
    stack = _stack(state)
    _require(stack[-len(ids):] == ids, "group must reverse the exact completed global suffix")
    originals = [_action(state, aid) for aid in ids]
    _require(len({x["document_id"] for x in originals}) == 1, "group compensation crosses document scope")
    for index, a in enumerate(originals):
        if index:
            _require(a["before"]["native_sha256"] == originals[index - 1]["after_sha256"], "group native history is not contiguous")
        inverse = a["inverse_requests"]
        if isinstance(inverse, dict) and inverse.get("kind") == "GROUP_ONLY":
            _require(inverse["group_anchor_action_id"] in ids[:index], "group omits its required creation anchor")
    return originals


def _group_verifier(value):
    _keys(value, {"verifier_id", "parameters"}, "group compensation verifier")
    _id(value["verifier_id"], "group verifier ID")
    _require(isinstance(value["parameters"], dict), "group verifier parameters absent")


def _reduce(previous, event, generation, binding):
    """Replay every event; a mutable final projection cannot rewrite history."""
    _keys(event, {"kind", "actor_id", "lease_id", "at", "details"}, "event")
    _id(event["actor_id"], "actor")
    now = _instant(event["at"])
    kind, d = event["kind"], event["details"]
    _require(isinstance(d, dict), "event details absent")
    s = copy.deepcopy(previous)
    if kind == "INITIALIZED":
        _require(previous is None and generation == 1 and event["lease_id"] is None, "invalid genesis")
        _keys(d, {"documents"}, "initialization")
        _require(set(d["documents"]) == set(binding.scope_document_ids), "initial scope differs")
        for pin in d["documents"].values():
            _keys(pin, {"revision_id", "native_sha256"}, "document pin")
            _require(isinstance(pin["revision_id"], str) and pin["revision_id"], "document revision absent")
            _sha(pin["native_sha256"])
        return {"phase": "IDLE", "lease": None, "documents": copy.deepcopy(d["documents"]),
                "actions": [], "hold": None, "release_projection": {
                    "stage": "UNAPPROVED", "standard_active": "UNVERIFIED",
                    "canonical_written_version": "UNVERIFIED", "activation_performed": False}}
    _require(s is not None, "genesis missing")
    if kind == "ACQUIRED":
        _keys(d, {"expires_at", "scope_document_ids"}, "acquisition")
        _id(event["lease_id"], "lease ID")
        _require(s["lease"] is None or s["lease"]["status"] == "CLOSED", "lease already held; no takeover")
        _require(not _unresolved(s) and s["hold"] is None, "unresolved previous execution")
        _require(d["scope_document_ids"] == list(binding.scope_document_ids), "lease scope differs")
        _require(now < _instant(d["expires_at"]), "expired acquisition")
        s["lease"] = {"holder_id": event["actor_id"], "lease_id": event["lease_id"],
                      "acquired_generation": generation, "expires_at": d["expires_at"], "status": "ACTIVE"}
        s["phase"] = "EXECUTING"
        return s
    readonly_completion = kind in {"ACKNOWLEDGED", "ACK_RECOVERED", "APPLIED", "UNKNOWN", "OBSERVED", "HELD", "REJECTED"}
    _owned(s, event["actor_id"], event["lease_id"], now,
           allow_expired=readonly_completion, allow_hold=readonly_completion or kind == "RESUMED")
    if kind == "RENEWED":
        _keys(d, {"expires_at"}, "renewal")
        _require(not _unresolved(s), "cannot renew during an in-flight action")
        _require(_instant(d["expires_at"]) > max(now, _instant(s["lease"]["expires_at"])), "renewal does not extend lease")
        s["lease"]["expires_at"] = d["expires_at"]
    elif kind == "LEASE_CLOSED":
        _keys(d, set(), "lease close")
        _require(not _unresolved(s), "cannot close an in-flight lease")
        s["lease"]["status"] = "CLOSED"
        s["phase"] = "QUIESCENT"
    elif kind == "PREPARED":
        _keys(d, {"action"}, "prepared")
        a = d["action"]
        fields = {"action_id", "document_id", "plan_sha256", "kind", "compensates", "requests",
                  "postcondition", "inverse_requests", "before", "status", "after_revision", "after_sha256"}
        if a.get("kind") == "COMPENSATE_GROUP":
            fields.add("compensation_verifier")
        _keys(a, fields, "action")
        _id(a["action_id"], "action ID")
        _require(not any(x["action_id"] == a["action_id"] for x in s["actions"]), "action ID reused")
        _require(not _unresolved(s), "another action is in flight")
        _require(a["document_id"] in binding.scope_document_ids, "action outside canonical Doc scope")
        _sha(a["plan_sha256"])
        _requests(a["requests"])
        if a["kind"] == "COMPENSATE_GROUP":
            _require(a["inverse_requests"] is None, "group compensation has no automatic redo inverse")
            _group_verifier(a["compensation_verifier"])
        else:
            _inverse_spec(a["inverse_requests"])
        _postcondition(a["postcondition"])
        _require(a["before"] == s["documents"][a["document_id"]], "manifest and before-state differ")
        _require(a["status"] == "PREPARED" and a["after_revision"] is None and a["after_sha256"] is None, "prepared outcome fabricated")
        if a["kind"] == "COMPENSATE":
            stack = _stack(s)
            _require(stack and stack[-1] == a["compensates"], "rollback must reverse actual completed actions")
            original = _action(s, a["compensates"])
            _require(a["document_id"] == original["document_id"] and a["requests"] == _effective_inverse(original) and
                     a["postcondition"] == {"kind": "EXACT_NATIVE_STATE", "sha256": original["before"]["native_sha256"]}, "inverse differs from owned action")
            _require(a["before"]["native_sha256"] == original["after_sha256"], "rollback is not at the owned after-state")
        elif a["kind"] == "COMPENSATE_GROUP":
            originals = _group_actions(s, a["compensates"])
            _require(a["document_id"] == originals[0]["document_id"] and
                     a["postcondition"] == {"kind": "EXACT_NATIVE_STATE", "sha256": originals[0]["before"]["native_sha256"]},
                     "group compensation must restore the complete before-state of its first action")
            _require(a["before"]["native_sha256"] == originals[-1]["after_sha256"], "group is not at its owned after-state")
        else:
            _require(a["kind"] == "APPLY" and a["compensates"] is None, "unknown action kind")
            _group_only_anchor(s, a)
        if a["kind"] in {"COMPENSATE", "COMPENSATE_GROUP"}:
            p = s["release_projection"]
            _require(not p["activation_performed"] or
                     (p["standard_active"] == "1.13" and p["stage"] == "ROLLBACK_IN_PROGRESS"), "operative reversion required before physical rollback")
            s["phase"] = "ROLLING_BACK"
        else:
            s["phase"] = "EXECUTING"
        s["actions"].append(copy.deepcopy(a))
    elif kind in {"DISPATCHED", "ACKNOWLEDGED", "ACK_RECOVERED", "APPLIED", "REJECTED", "UNKNOWN"}:
        transition_fields = {"DISPATCHED": {"action_id"}, "ACKNOWLEDGED": {"action_id", "after_revision"},
                             "ACK_RECOVERED": {"action_id", "after_revision"},
                             "APPLIED": {"action_id", "after_revision", "after_sha256"},
                             "REJECTED": {"action_id", "reason"}, "UNKNOWN": {"action_id", "reason"}}
        a = _action(s, d["action_id"])
        if kind == "APPLIED" and _deferred_inverse(a):
            transition_fields[kind].add("resolved_inverse_requests")
        _keys(d, transition_fields[kind], kind)
        expected = {"DISPATCHED": "PREPARED", "ACKNOWLEDGED": "DISPATCHED", "APPLIED": "ACKNOWLEDGED",
                    "ACK_RECOVERED": None, "REJECTED": "DISPATCHED", "UNKNOWN": "DISPATCHED"}[kind]
        _require(a["status"] in {"DISPATCHED", "UNKNOWN"} if kind == "ACK_RECOVERED" else a["status"] == expected,
                 "invalid action transition; redispatch forbidden")
        if kind in {"ACKNOWLEDGED", "ACK_RECOVERED"}:
            _require(isinstance(d["after_revision"], str) and d["after_revision"] and
                     d["after_revision"] != a["before"]["revision_id"], "new acknowledged revision absent")
            a["after_revision"] = d["after_revision"]
        if kind == "APPLIED":
            _sha(d["after_sha256"])
            _require(d["after_revision"] == a["after_revision"], "ack/readback revision differs")
            a["after_sha256"] = d["after_sha256"]
            if _deferred_inverse(a):
                _requests(d["resolved_inverse_requests"])
                a["resolved_inverse_requests"] = copy.deepcopy(d["resolved_inverse_requests"])
            s["documents"][a["document_id"]] = {"revision_id": d["after_revision"], "native_sha256": d["after_sha256"]}
        a["status"] = {"REJECTED": "NOT_APPLIED", "ACK_RECOVERED": "ACKNOWLEDGED"}.get(kind, kind)
        if kind in {"REJECTED", "UNKNOWN"}:
            s["hold"] = {"reason": d["reason"], "action_id": a["action_id"]}
            s["phase"] = "HOLD"
    elif kind == "HELD":
        _keys(d, {"reason", "action_id"}, "hold")
        _require(isinstance(d["reason"], str) and d["reason"], "hold reason absent")
        if d["action_id"] is not None:
            _action(s, d["action_id"])
        s["hold"] = copy.deepcopy(d)
        s["phase"] = "HOLD"
    elif kind == "OBSERVED":
        _keys(d, {"action_id", "classification", "pin"}, "observation")
        a = _action(s, d["action_id"])
        _require(a["status"] in {"DISPATCHED", "UNKNOWN", "ACKNOWLEDGED"}, "no uncertain action to observe")
        _require(d["classification"] in {"BEFORE", "AFTER", "OTHER"}, "unknown observation class")
        s["hold"] = {"reason": "read-only observation does not authenticate a missing acknowledgement", "action_id": a["action_id"]}
        s["phase"] = "HOLD"
    elif kind == "RESUMED":
        _keys(d, {"reason"}, "resume")
        _require(not _unresolved(s) and s["hold"] is not None, "only resolved known outcomes can resume")
        s["hold"] = None
        s["phase"] = "EXECUTING"
    elif kind == "RELEASE_PROJECTION_RECORDED":
        _keys(d, {"projection"}, "projection event")
        _require(not _unresolved(s), "projection blocked by incomplete native action")
        p = d["projection"]
        _projection(p)
        _require(not s["release_projection"]["activation_performed"] or p["activation_performed"], "activation history cannot be erased")
        s["release_projection"] = copy.deepcopy(p)
    else:
        raise Hold("unknown coordinator event")
    return s


class Coordinator:
    """Transport and policy injection are trust boundaries, never owner decisions.

    authority_check(binding) must verify the one authoritative location and
    no-rewind/no-delete writer policy. policy_check(purpose, exact_payload)
    authenticates an existing exact plan/permission and returns its raw evidence.
    No default policy permits Docs mutations or release-projection changes.
    """

    def __init__(self, git: GitTransport, docs: DocsTransport, binding: Binding, *,
                 authority_check: Callable[[Binding], bool] | None = None,
                 policy_check: Callable[[str, dict], bytes] | None = None,
                 clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
                 postcondition_verifiers: Mapping[str, Callable[[dict, dict, dict, dict], bool]] | None = None,
                 inverse_resolvers: Mapping[str, Callable[[dict, dict, dict, dict], list[dict]]] | None = None,
                 group_compensation_verifiers: Mapping[str, Callable[[dict, list[dict], list[dict], dict, list[dict]], bool]] | None = None):
        self.git, self.docs, self.binding = git, docs, binding
        self.authority_check, self.policy_check, self.clock = authority_check, policy_check, clock
        self.verifiers = dict(postcondition_verifiers or {})
        self.inverse_resolvers = dict(inverse_resolvers or {})
        self.group_verifiers = dict(group_compensation_verifiers or {})
        self._last_clock: datetime | None = None

    def _now(self):
        now = _instant(_stamp(self.clock()))
        _require(self._last_clock is None or now >= self._last_clock, "clock moved backwards")
        self._last_clock = now
        return now

    def _authority(self):
        check = self.authority_check
        if not callable(check):
            raise Hold("authoritative ref policy not verified")
        _require(check(self.binding) is True, "authoritative ref policy not verified")

    def _policy(self, purpose, payload):
        check = self.policy_check
        if not callable(check):
            raise Hold("exact external policy/permission verifier unavailable")
        raw = check(purpose, copy.deepcopy(payload))
        _require(isinstance(raw, bytes) and raw, "exact external policy/permission not authenticated")
        return raw

    def _manifest(self, generation, previous_head, state, refs):
        return {"schema": SCHEMA, "binding": self.binding.record(), "generation": generation,
                "previous_head": previous_head, "state": state, "receipts": refs}

    def _verify_after(self, action, before, ack, after):
        _, pin = native_state(after, action["document_id"])
        condition = action["postcondition"]
        if condition["kind"] == "EXACT_NATIVE_STATE":
            _require(pin["native_sha256"] == condition["sha256"], "full native after-state differs")
        else:
            verifier = self.verifiers.get(condition["verifier_id"])
            if not callable(verifier):
                raise Hold("registered native postcondition verifier unavailable")
            _require(verifier(copy.deepcopy(condition["parameters"]), parse_json(before), parse_json(ack), parse_json(after)) is True,
                     "registered native transform was not verified")
        return pin

    def _resolve_inverse(self, action, before, ack, after):
        descriptor = action["inverse_requests"]
        _require(_deferred_inverse(action), "inverse is not a registered deferred inverse")
        resolver = self.inverse_resolvers.get(descriptor["resolver_id"])
        if not callable(resolver):
            raise Hold("registered native inverse resolver unavailable")
        resolved = resolver(copy.deepcopy(descriptor["parameters"]), parse_json(before), parse_json(ack), parse_json(after))
        _requests(resolved)
        return copy.deepcopy(resolved)

    def _verify_group(self, state, action, archives, before):
        originals = _group_actions(state, action["compensates"])
        descriptor = action["compensation_verifier"]
        _group_verifier(descriptor)
        verifier = self.group_verifiers.get(descriptor["verifier_id"])
        if not callable(verifier):
            raise Hold("registered group compensation verifier unavailable")
        history = [{"action_id": original["action_id"], **{
            kind: parse_json(archives[original["action_id"]][kind]) for kind in ("before", "ack", "after")}}
                   for original in originals]
        _require(verifier(copy.deepcopy(descriptor["parameters"]), copy.deepcopy(originals), history,
                          parse_json(before), copy.deepcopy(action["requests"])) is True,
                 "owned group compensation was not verified")

    def _evidence_check(self, event, evidence, previous, archives):
        kind, d = event["kind"], event["details"]
        if kind == "INITIALIZED":
            for doc_id, pin in d["documents"].items():
                _require(native_state(evidence["document:" + doc_id], doc_id)[1] == pin, "initial document evidence differs")
        elif kind == "PREPARED":
            a = d["action"]
            _require(native_state(evidence["before"], a["document_id"])[1] == a["before"], "prepared before evidence differs")
            _require(evidence.get("permission"), "prepared permission evidence absent")
            for doc_id, pin in previous["documents"].items():
                _require(native_state(evidence["document:" + doc_id], doc_id)[1] == pin, "prepared scope readback differs")
            if a["kind"] == "COMPENSATE_GROUP":
                self._verify_group(previous, a, archives, evidence["before"])
            archives[a["action_id"]] = {"before": evidence["before"]}
        elif kind == "DISPATCHED":
            a = _action(previous, d["action_id"])
            _require(native_state(evidence["before"], a["document_id"])[1] == a["before"], "dispatch revision/content drift")
            request = parse_json(evidence["request"])
            _require(request == {"requests": a["requests"], "writeControl": {"requiredRevisionId": a["before"]["revision_id"]}}, "per-document requiredRevisionId differs")
            _require(evidence.get("permission"), "dispatch permission evidence absent")
            for doc_id, pin in previous["documents"].items():
                _require(native_state(evidence["document:" + doc_id], doc_id)[1] == pin, "dispatch scope readback differs")
        elif kind in {"ACKNOWLEDGED", "ACK_RECOVERED"}:
            a = _action(previous, d["action_id"])
            if kind == "ACK_RECOVERED":
                _require(evidence.get("permission") and evidence.get("provenance"), "missing-ack origin not authenticated")
            ack = parse_json(evidence["response"])
            _require(_ack_revision(ack, a["document_id"]) == d["after_revision"], "ack identity/revision absent or differs")
            archives[a["action_id"]]["ack"] = evidence["response"]
        elif kind == "APPLIED":
            a = _action(previous, d["action_id"])
            saved = archives[a["action_id"]]
            pin = self._verify_after(a, saved["before"], saved["ack"], evidence["after"])
            _require(pin == {"revision_id": d["after_revision"], "native_sha256": d["after_sha256"]}, "applied readback evidence differs")
            if _deferred_inverse(a):
                resolved = self._resolve_inverse(a, saved["before"], saved["ack"], evidence["after"])
                _require(resolved == d["resolved_inverse_requests"], "bound inverse differs from full actual native evidence")
            for doc_id, expected in previous["documents"].items():
                if doc_id != a["document_id"]:
                    _require(native_state(evidence["document:" + doc_id], doc_id)[1] == expected, "applied cohort readback differs")
            archives[a["action_id"]]["after"] = evidence["after"]
        elif kind == "OBSERVED":
            a = _action(previous, d["action_id"])
            _require(native_state(evidence["observed"], a["document_id"])[1] == d["pin"], "observation evidence differs")
        elif kind in {"RELEASE_PROJECTION_RECORDED", "RESUMED"}:
            _require(evidence.get("permission"), "projection/recovery permission evidence absent")
            for doc_id, pin in previous["documents"].items():
                _require(native_state(evidence["document:" + doc_id], doc_id)[1] == pin, "projection and full live Docs differ")
        elif kind == "REJECTED":
            _require(evidence.get("response"), "definite rejection response absent")

    @_fail_closed
    def read(self, checkpoint: Checkpoint | None = None):
        """Fresh remote ref, immutable Git objects, complete event replay/readback."""
        self._authority()
        head = self.git.read_head()
        _sha(head, SHA1)
        if checkpoint is not None:
            _require(type(checkpoint.generation) is int and checkpoint.generation > 0, "invalid expected generation")
            _require(checkpoint.head == head, "stale expected head")
        snap = self.git.snapshot(head)
        _require(snap.head == head, "snapshot head differs")
        try:
            raw = snap.files[self.binding.manifest_path]
            m = parse_json(raw)
            _keys(m, {"schema", "binding", "generation", "previous_head", "state", "receipts"}, "manifest")
            _require(m["schema"] == SCHEMA and m["binding"] == self.binding.record(), "manifest authority/scope binding differs")
            _require(type(m["generation"]) is int and m["generation"] > 0 and isinstance(m["receipts"], list) and
                     len(m["receipts"]) == m["generation"], "generation/history length differs")
            if checkpoint is not None:
                _require(m["generation"] == checkpoint.generation, "stale expected generation")
            state, previous_head, previous_receipt, at = None, self.binding.anchor_head, None, None
            archives: dict[str, dict[str, bytes]] = {}
            expected_files, prefix, used_leases = {}, [], set()
            previous_entries = self.git.snapshot(self.binding.anchor_head).entries
            _require(not any(p.startswith(self.binding.namespace + "/") for p in previous_entries), "anchor already has a coordinator namespace")
            for i, ref in enumerate(m["receipts"], 1):
                _keys(ref, {"path", "sha256", "generation", "previous_head"}, "receipt ref")
                path = self.binding.namespace + "/receipts/" + f"{i:08d}.json"
                _require(ref["path"] == path and ref["generation"] == i and type(ref["generation"]) is int and
                         ref["previous_head"] == previous_head, "receipt order/parent differs")
                receipt_raw = snap.files[path]
                _require(digest(receipt_raw) == ref["sha256"], "receipt bytes differ")
                receipt = parse_json(receipt_raw)
                _keys(receipt, {"schema", "generation", "previous_head", "previous_receipt_sha256", "before_state_sha256",
                                "event", "state_after", "evidence"}, "receipt")
                _require(receipt["schema"] == SCHEMA + "/receipt" and type(receipt["generation"]) is int and receipt["generation"] == i and
                         receipt["previous_head"] == previous_head and receipt["previous_receipt_sha256"] == previous_receipt and
                         receipt["before_state_sha256"] == (digest(json_bytes(state)) if state is not None else None), "receipt chain differs")
                event = receipt["event"]
                event_time = _instant(event["at"])
                _require((at is None or event_time >= at) and event_time <= self._now(), "receipt chronology differs")
                at = event_time
                if event["kind"] == "ACQUIRED":
                    _require(event["lease_id"] not in used_leases, "lease token reused")
                    used_leases.add(event["lease_id"])
                evidence = {k: _unpacked(v) for k, v in receipt["evidence"].items()}
                self._evidence_check(event, evidence, state, archives)
                state = _reduce(state, event, i, self.binding)
                _require(state == receipt["state_after"], "receipt projection differs from replay")
                prefix.append(ref)
                old_manifest = self._manifest(i, previous_head, state, list(prefix))
                expected_files[path] = receipt_raw
                expected_files[self.binding.manifest_path] = json_bytes(old_manifest)
                commit_head = m["receipts"][i]["previous_head"] if i < len(m["receipts"]) else head
                historical = self.git.snapshot(commit_head)
                _require(historical.parents == (previous_head,), "coordinator commit must have exactly its expected parent")
                wanted_entries = dict(previous_entries)
                wanted_entries[path] = ("100644", git_blob_sha(receipt_raw))
                wanted_entries[self.binding.manifest_path] = ("100644", git_blob_sha(expected_files[self.binding.manifest_path]))
                _require(dict(historical.entries) == wanted_entries, "atomic commit scope/history differs")
                previous_entries = historical.entries
                previous_head, previous_receipt = commit_head, ref["sha256"]
            _require(m["state"] == state and m["previous_head"] == m["receipts"][-1]["previous_head"] and
                     raw == json_bytes(self._manifest(m["generation"], m["previous_head"], state, m["receipts"])), "manifest projection differs")
            _require(dict(snap.files) == expected_files, "coordinator namespace contains missing/extra/changed bytes")
            _require(self.git.read_head() == head, "head moved during readback")
            return Checkpoint(head, m["generation"]), m, archives
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise Hold("malformed or incomplete coordinator evidence") from exc

    def _publish(self, checkpoint, manifest, kind, actor, lease_id, details, evidence):
        self._authority()
        generation = 1 if manifest is None else manifest["generation"] + 1
        expected = self.binding.anchor_head if checkpoint is None else checkpoint.head
        event = {"kind": kind, "actor_id": actor, "lease_id": lease_id, "at": _stamp(self._now()), "details": details}
        previous = None if manifest is None else manifest["state"]
        state = _reduce(previous, event, generation, self.binding)
        refs = [] if manifest is None else copy.deepcopy(manifest["receipts"])
        receipt = {"schema": SCHEMA + "/receipt", "generation": generation, "previous_head": expected,
                   "previous_receipt_sha256": refs[-1]["sha256"] if refs else None,
                   "before_state_sha256": digest(json_bytes(previous)) if previous is not None else None,
                   "event": event, "state_after": state, "evidence": {k: _packed(v) for k, v in evidence.items()}}
        path = self.binding.namespace + "/receipts/" + f"{generation:08d}.json"
        raw = json_bytes(receipt)
        refs.append({"path": path, "sha256": digest(raw), "generation": generation, "previous_head": expected})
        new_manifest = self._manifest(generation, expected, state, refs)
        changes = {path: raw, self.binding.manifest_path: json_bytes(new_manifest)}
        _require(self.git.read_head() == expected, "stale expected head before publish")
        candidate = None
        try:
            candidate = self.git.create_commit(expected, changes, f"coordinator {generation}: {kind}")
            _sha(candidate, SHA1)
            before, after = self.git.snapshot(expected), self.git.snapshot(candidate)
            wanted = dict(before.entries)
            wanted.update({p: ("100644", git_blob_sha(b)) for p, b in changes.items()})
            _require(after.parents == (expected,) and dict(after.entries) == wanted and
                     all(after.files.get(p) == b for p, b in changes.items()), "candidate commit readback differs")
            ack = self.git.update_ref(expected, candidate)
            _require(ack == candidate, "ref acknowledgement differs")
            result, _, _ = self.read(Checkpoint(candidate, generation))
            return result
        except Exception as exc:
            # Never retry here, even if a subsequent read might find the commit.
            raise Hold("Git publication is rejected or uncertain: " + str(exc), attempted_head=candidate) from exc

    @_fail_closed
    def initialize(self, actor_id="coordinator"):
        _require(self.git.read_head() == self.binding.anchor_head, "initialization requires the exact trusted anchor")
        _require(not any(p.startswith(self.binding.namespace + "/") for p in self.git.snapshot(self.binding.anchor_head).entries), "coordinator already exists")
        documents, evidence = {}, {}
        for doc_id in self.binding.scope_document_ids:
            raw = self.docs.get_document(doc_id)
            documents[doc_id] = native_state(raw, doc_id)[1]
            evidence["document:" + doc_id] = raw
        return self._publish(None, None, "INITIALIZED", actor_id, None, {"documents": documents}, evidence)

    @_fail_closed
    def acquire(self, checkpoint, holder_id, lease_id, expires_at, scope_document_ids):
        cp, m, _ = self.read(checkpoint)
        _require(not any(parse_json(self.git.snapshot(cp.head).files[r["path"]])["event"]["lease_id"] == lease_id for r in m["receipts"]), "lease token reused")
        return self._publish(cp, m, "ACQUIRED", holder_id, lease_id,
                             {"expires_at": expires_at, "scope_document_ids": list(scope_document_ids)}, {})

    @_fail_closed
    def renew(self, checkpoint, holder_id, lease_id, expires_at):
        cp, m, _ = self.read(checkpoint)
        return self._publish(cp, m, "RENEWED", holder_id, lease_id, {"expires_at": expires_at}, {})

    @_fail_closed
    def release(self, checkpoint, holder_id, lease_id):
        cp, m, _ = self.read(checkpoint)
        return self._publish(cp, m, "LEASE_CLOSED", holder_id, lease_id, {}, {})

    def _fresh_all(self, state):
        evidence = {}
        for doc_id, pin in state["documents"].items():
            raw = self.docs.get_document(doc_id)
            _require(native_state(raw, doc_id)[1] == pin, "manifest and live Docs diverge: " + doc_id)
            evidence["document:" + doc_id] = raw
        return evidence

    @_fail_closed
    def prepare_action(self, checkpoint, holder_id, lease_id, spec: ActionSpec, *, compensates=None):
        _require(compensates is None or isinstance(compensates, str), "use prepare_group_compensation for a reviewed group")
        return self._prepare_action(checkpoint, holder_id, lease_id, spec, compensates=compensates)

    def _prepare_action(self, checkpoint, holder_id, lease_id, spec, *, compensates=None, compensation_verifier=None):
        cp, m, archives = self.read(checkpoint)
        _owned(m["state"], holder_id, lease_id, self._now())
        _require(spec.document_id in self.binding.scope_document_ids, "document outside canonical scope")
        all_docs = self._fresh_all(m["state"])
        raw = all_docs["document:" + spec.document_id]
        a = {"action_id": spec.action_id, "document_id": spec.document_id, "plan_sha256": spec.plan_sha256,
             "kind": "COMPENSATE_GROUP" if compensation_verifier is not None else ("COMPENSATE" if compensates is not None else "APPLY"),
             "compensates": copy.deepcopy(compensates),
             "requests": copy.deepcopy(spec.requests), "postcondition": copy.deepcopy(spec.postcondition),
             "inverse_requests": copy.deepcopy(spec.inverse_requests), "before": native_state(raw, spec.document_id)[1],
             "status": "PREPARED", "after_revision": None, "after_sha256": None}
        if compensation_verifier is not None:
            a["compensation_verifier"] = copy.deepcopy(compensation_verifier)
            self._verify_group(m["state"], a, archives, raw)
        else:
            _inverse_spec(a["inverse_requests"])
            if _deferred_inverse(a):
                _require(callable(self.inverse_resolvers.get(a["inverse_requests"]["resolver_id"])), "native inverse resolver unavailable")
        _postcondition(a["postcondition"])
        if a["postcondition"]["kind"] == "REGISTERED_NATIVE_TRANSFORM":
            _require(callable(self.verifiers.get(a["postcondition"]["verifier_id"])), "native verifier unavailable")
        permission = self._policy("prepare_compensation" if compensates else "prepare_action", {"binding": self.binding.record(), "action": a, "release_projection": m["state"]["release_projection"]})
        return self._publish(cp, m, "PREPARED", holder_id, lease_id, {"action": a},
                             {"before": raw, "permission": permission, **all_docs})

    @_fail_closed
    def dispatch(self, checkpoint, holder_id, lease_id, action_id):
        cp, m, _ = self.read(checkpoint)
        _owned(m["state"], holder_id, lease_id, self._now())
        a = _action(m["state"], action_id)
        _require(a["status"] == "PREPARED", "redispatch forbidden; recover read-only")
        all_docs = self._fresh_all(m["state"])
        permission = self._policy("dispatch", {"binding": self.binding.record(), "action": a, "release_projection": m["state"]["release_projection"]})
        body = {"requests": copy.deepcopy(a["requests"]), "writeControl": {"requiredRevisionId": a["before"]["revision_id"]}}
        cp = self._publish(cp, m, "DISPATCHED", holder_id, lease_id, {"action_id": action_id},
                           {"before": all_docs["document:" + a["document_id"]], "request": json_bytes(body),
                            "permission": permission, **all_docs})
        # Only this call, after its acknowledged winning CAS, can dispatch.
        cp, m, _ = self.read(cp)
        _owned(m["state"], holder_id, lease_id, self._now())
        self._fresh_all(m["state"])
        _require(self.git.read_head() == cp.head, "head moved before native effect")
        self._authority()
        _owned(m["state"], holder_id, lease_id, self._now())
        try:
            raw = self.docs.batch_update(a["document_id"], body)
        except Rejected as exc:
            self._publish(cp, m, "REJECTED", holder_id, lease_id,
                          {"action_id": action_id, "reason": str(exc)}, {"response": exc.raw})
            raise Hold("Docs rejected; execution is on HOLD") from exc
        except Exception as exc:
            self._publish(cp, m, "UNKNOWN", holder_id, lease_id,
                          {"action_id": action_id, "reason": "native outcome/acknowledgement unknown"}, {})
            raise Hold("Docs outcome unknown; redispatch forbidden") from exc
        try:
            ack = parse_json(raw)
            revision = _ack_revision(ack, a["document_id"])
        except Exception as exc:
            self._publish(cp, m, "UNKNOWN", holder_id, lease_id,
                          {"action_id": action_id, "reason": "native acknowledgement malformed"}, {"response": raw})
            raise Hold("native acknowledgement malformed") from exc
        return self._publish(cp, m, "ACKNOWLEDGED", holder_id, lease_id,
                             {"action_id": action_id, "after_revision": revision}, {"response": raw})

    @_fail_closed
    def complete_readback(self, checkpoint, holder_id, lease_id, action_id):
        """May finish a durable ACK after restart/expiry; never writes to Docs."""
        cp, m, archives = self.read(checkpoint)
        _owned(m["state"], holder_id, lease_id, self._now(), allow_expired=True, allow_hold=True)
        a = _action(m["state"], action_id)
        _require(a["status"] == "ACKNOWLEDGED", "authenticated durable acknowledgement required")
        raw = self.docs.get_document(a["document_id"])
        evidence = {"after": raw}
        try:
            pin = self._verify_after(a, archives[action_id]["before"], archives[action_id]["ack"], raw)
            _require(pin["revision_id"] == a["after_revision"], "native readback is not the acknowledged revision")
            details = {"action_id": action_id, "after_revision": pin["revision_id"], "after_sha256": pin["native_sha256"]}
            if _deferred_inverse(a):
                details["resolved_inverse_requests"] = self._resolve_inverse(a, archives[action_id]["before"], archives[action_id]["ack"], raw)
            for doc_id, expected in m["state"]["documents"].items():
                if doc_id != a["document_id"]:
                    other = self.docs.get_document(doc_id)
                    evidence["document:" + doc_id] = other
                    _require(native_state(other, doc_id)[1] == expected, "another scoped document diverged")
        except Exception as exc:
            self._publish(cp, m, "HELD", holder_id, lease_id,
                          {"action_id": action_id, "reason": str(exc)}, {"observed": raw})
            raise Hold("readback differs; actual acknowledgement remains in history") from exc
        return self._publish(cp, m, "APPLIED", holder_id, lease_id, details, evidence)

    @_fail_closed
    def observe_uncertain(self, checkpoint, holder_id, lease_id, action_id):
        """Record actual bytes; even matching AFTER cannot invent a missing ack."""
        cp, m, archives = self.read(checkpoint)
        _owned(m["state"], holder_id, lease_id, self._now(), allow_expired=True, allow_hold=True)
        a = _action(m["state"], action_id)
        raw = self.docs.get_document(a["document_id"])
        pin = native_state(raw, a["document_id"])[1]
        classification = "BEFORE" if pin == a["before"] else "OTHER"
        if a["postcondition"]["kind"] == "EXACT_NATIVE_STATE" and pin["native_sha256"] == a["postcondition"]["sha256"]:
            classification = "AFTER"
        return self._publish(cp, m, "OBSERVED", holder_id, lease_id,
                             {"action_id": action_id, "classification": classification, "pin": pin}, {"observed": raw})

    @_fail_closed
    def recover_git_ack(self, previous_head, attempted_head):
        """Explicit read-only recovery, only when the exact candidate is current."""
        _sha(previous_head, SHA1)
        _sha(attempted_head, SHA1)
        _require(self.git.read_head() == attempted_head, "attempted commit is not the current authoritative head")
        cp, m, _ = self.read()
        _require(m["previous_head"] == previous_head, "recovery candidate parent differs")
        return cp

    @_fail_closed
    def recover_native_ack(self, checkpoint, holder_id, lease_id, action_id, response: bytes, provenance: bytes):
        """Explicit intake of an authentic saved response; matching content is insufficient.

        This appends the actual acknowledgement and keeps HOLD. Full readback and
        a separately reviewed resume follow; no native mutation is attempted.
        """
        cp, m, _ = self.read(checkpoint)
        _owned(m["state"], holder_id, lease_id, self._now(), allow_expired=True, allow_hold=True)
        a = _action(m["state"], action_id)
        ack = parse_json(response)
        revision = _ack_revision(ack, a["document_id"])
        permission = self._policy("recover_native_ack", {"binding": self.binding.record(), "action": a,
                                   "response": _packed(response), "provenance": _packed(provenance)})
        return self._publish(cp, m, "ACK_RECOVERED", holder_id, lease_id,
                             {"action_id": action_id, "after_revision": revision},
                             {"response": response, "provenance": provenance, "permission": permission})

    @_fail_closed
    def resume_known_outcomes(self, checkpoint, holder_id, lease_id, reason):
        cp, m, _ = self.read(checkpoint)
        _owned(m["state"], holder_id, lease_id, self._now(), allow_hold=True)
        evidence = self._fresh_all(m["state"])
        evidence["permission"] = self._policy("resume_known_outcomes", {"binding": self.binding.record(), "state": m["state"], "reason": reason})
        return self._publish(cp, m, "RESUMED", holder_id, lease_id, {"reason": reason}, evidence)

    @_fail_closed
    def prepare_compensation(self, checkpoint, holder_id, lease_id, new_action_id, compensates, plan_sha256):
        _, m, _ = self.read(checkpoint)
        original = _action(m["state"], compensates)
        spec = ActionSpec(new_action_id, original["document_id"], plan_sha256,
                          _effective_inverse(original), {"kind": "EXACT_NATIVE_STATE", "sha256": original["before"]["native_sha256"]}, original["requests"])
        return self.prepare_action(checkpoint, holder_id, lease_id, spec, compensates=compensates)

    @_fail_closed
    def prepare_group_compensation(self, checkpoint, holder_id, lease_id, new_action_id,
                                   compensates, plan_sha256, requests, compensation_verifier):
        """Compensate an authenticated contiguous owned suffix in one document.

        A pinned verifier proves the exact grouped operation from complete native
        history. The result must be the first action's full before-state; no fake
        intermediate undo, removed history, cross-document batch, or redo exists.
        """
        _, m, _ = self.read(checkpoint)
        originals = _group_actions(m["state"], compensates)
        first = originals[0]
        spec = ActionSpec(new_action_id, first["document_id"], plan_sha256, requests,
                          {"kind": "EXACT_NATIVE_STATE", "sha256": first["before"]["native_sha256"]}, None)
        return self._prepare_action(checkpoint, holder_id, lease_id, spec, compensates=compensates,
                                    compensation_verifier=compensation_verifier)

    @_fail_closed
    def record_release_projection(self, checkpoint, holder_id, lease_id, projection):
        cp, m, _ = self.read(checkpoint)
        _owned(m["state"], holder_id, lease_id, self._now())
        evidence = self._fresh_all(m["state"])
        evidence["permission"] = self._policy("release_projection", {"binding": self.binding.record(), "before": m["state"], "projection": projection})
        cp = self._publish(cp, m, "RELEASE_PROJECTION_RECORDED", holder_id, lease_id, {"projection": projection}, evidence)
        _, current, _ = self.read(cp)
        try:
            self._fresh_all(current["state"])
        except Exception as exc:
            self._publish(cp, current, "HELD", holder_id, lease_id,
                          {"reason": "Docs diverged during projection publication", "action_id": None}, {})
            raise Hold("Docs diverged during projection publication; actual projection remains in history") from exc
        return cp


class GitHubTransport:
    """Connector adapter: call(operation, arguments) -> decoded API JSON object.

    Names map to github_fetch/fetch_blob/create_blob/create_tree/create_commit/update_ref.
    The adapter never creates/deletes branches or uses force=true. Its object
    caches are immutable; every authority check reads the remote ref afresh.
    """

    def __init__(self, binding: Binding, call: Callable):
        self.binding, self.call = binding, call
        self._commits: dict[str, dict] = {}
        self._trees: dict[str, dict[str, tuple[str, str]]] = {}
        self._blobs: dict[str, bytes] = {}

    def _fetch(self, suffix):
        return self.call("github_fetch", {"url": "https://api.github.com/repos/" + self.binding.repository + suffix})

    def read_head(self):
        obj = self._fetch("/git/ref/heads/" + quote(self.binding.branch, safe="/"))
        _require(obj.get("ref") == "refs/heads/" + self.binding.branch and obj.get("object", {}).get("type") == "commit", "authoritative ref response differs")
        return _sha(obj["object"]["sha"], SHA1)

    def snapshot(self, head):
        _sha(head, SHA1)
        if head not in self._commits:
            commit = self._fetch("/git/commits/" + head)
            _require(commit.get("sha") == head, "Git commit response differs")
            self._commits[head] = commit
        c = self._commits[head]
        tree_sha = c["tree"]["sha"]
        if tree_sha not in self._trees:
            tree = self._fetch("/git/trees/" + tree_sha + "?recursive=1")
            _require(tree.get("sha") == tree_sha and tree.get("truncated") is False, "incomplete Git tree response")
            entries = {}
            for e in tree["tree"]:
                if e["type"] == "tree":
                    continue
                _require(e["path"] not in entries and e["type"] in {"blob", "commit"}, "duplicate/unknown tree entry")
                entries[e["path"]] = (e["mode"], e["sha"])
            self._trees[tree_sha] = entries
        entries, files = self._trees[tree_sha], {}
        for path, (mode, sha) in entries.items():
            if not path.startswith(self.binding.namespace + "/"):
                continue
            _require(mode == "100644", "coordinator files must be regular non-executable blobs")
            if sha not in self._blobs:
                blob = self.call("github_fetch_blob", {"repository_full_name": self.binding.repository, "blob_sha": sha})
                _require(isinstance(blob, dict), "Git blob response absent")
                if set(blob) == {"content"}:
                    # Observed connector returns decoded UTF-8, without REST metadata.
                    # Never strip, normalize, add a newline, or fabricate sha/encoding.
                    _require(isinstance(blob["content"], str), "UTF-8 Git blob content absent")
                    raw = blob["content"].encode("utf-8")
                else:
                    # Direct REST transports may supply the actual base64 object.
                    _require(blob.get("sha") == sha and blob.get("encoding") == "base64", "raw Git blob encoding unavailable")
                    try:
                        raw = base64.b64decode("".join(blob["content"].splitlines()), validate=True)
                    except (ValueError, TypeError) as exc:
                        raise Hold("malformed Git blob") from exc
                    _require(type(blob.get("size")) is int and blob["size"] == len(raw), "Git blob byte count differs")
                _require(git_blob_sha(raw) == sha, "Git blob bytes differ")
                self._blobs[sha] = raw
            files[path] = self._blobs[sha]
        return Snapshot(head, tuple(p["sha"] for p in c["parents"]), tree_sha, dict(entries), files)

    def create_commit(self, parent, changes, message):
        before = self.snapshot(parent)
        elements = []
        for path, raw in sorted(changes.items()):
            _require(path.startswith(self.binding.namespace + "/"), "write outside coordinator namespace")
            blob = self.call("github_create_blob", {"repository_full_name": self.binding.repository, "content": raw.decode("utf-8"), "encoding": "utf-8"})
            _require(blob.get("sha") == git_blob_sha(raw), "created blob SHA differs")
            self._blobs[blob["sha"]] = raw
            elements.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        tree = self.call("github_create_tree", {"repository_full_name": self.binding.repository, "base_tree_sha": before.tree_sha, "tree_elements": elements})
        commit = self.call("github_create_commit", {"repository_full_name": self.binding.repository, "tree_sha": _sha(tree.get("sha"), SHA1),
                                                     "parent_sha": parent, "message": message})
        return _sha(commit.get("sha"), SHA1)

    def update_ref(self, expected, new):
        _require(self.snapshot(new).parents == (expected,), "non-linear candidate forbidden")
        _require(self.read_head() == expected, "expected head differs before ref request")
        result = self.call("github_update_ref", {"repository_full_name": self.binding.repository, "branch_name": self.binding.branch,
                                                 "expected_sha": expected, "sha": new, "force": False})
        _require(isinstance(result, dict), "ref acknowledgement absent")
        if "success" in result:
            _require(set(result) == {"success"} and result["success"] is True, "connector ref acknowledgement is not an unambiguous success")
        else:
            _require(result.get("ref") == "refs/heads/" + self.binding.branch and
                     result.get("object", {}).get("sha") == new, "ref acknowledgement identity differs")
        # success:true is the real connector acknowledgement, not a ref object.
        # An independent fresh GET supplies the SHA; never synthesize a REST ack.
        _require(self.read_head() == new, "ref readback does not confirm the acknowledged candidate")
        return new


class GoogleDocsTransport:
    """call('docs_get'|'docs_batch_update', exact API arguments) -> raw bytes.

    The runner must forward every argument, perform no response field filtering,
    and raise Rejected only for an authenticated no-effect HTTP rejection.
    """

    def __init__(self, call: Callable):
        self.call = call

    def get_document(self, document_id):
        return self.call("docs_get", {"documentId": document_id, "includeTabsContent": True})

    def batch_update(self, document_id, body):
        _keys(body, {"requests", "writeControl"}, "batch envelope")
        _keys(body["writeControl"], {"requiredRevisionId"}, "write control")
        return self.call("docs_batch_update", {"documentId": document_id, "body": copy.deepcopy(body)})
