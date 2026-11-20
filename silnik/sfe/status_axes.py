"""Preserved status vocabulary with strict release 2.0 evidence requirements.

SF-RULE-STA-001..005. Raw historical records are never rewritten or upgraded.
A historical permissive value is not consent for a new candidate.
The four positional arguments remain callable; missing v2 proof causes HOLD.
"""
from __future__ import annotations
from sfe import release_evidence as RE

ALLOWED = {
    "A": {"ROBOCZY", "UKOŃCZONY_PLIK"},
    "B": {"PALI_FIRST_UDOKUMENTOWANY", "PALI_FIRST_DEKLAROWANY", "EN_PL_HH", "EN_PL_INNY", "NIEUSTALONE"},
    "C": {"NIEUDOKUMENTOWANA", "CZĘŚCIOWA", "PEŁNA_AI", "PEŁNA_AUTOKONTROLA"},
    "D": {"BRAK", "ODSTĄPIONO", "CZĘŚCIOWA", "PEŁNA"},
    "E": {"WSTRZYMANE", "DOPUSZCZONE_JAKO_OPRACOWANIE_AI", "DOPUSZCZONE_PO_RECENZJI"},
}


def validate(axes: dict, owner: dict, coverage_ready: bool, human_review: str,
             *, root=None, evidence=None, author_contract=None) -> list[dict]:
    problems = []

    def bad(code, axis, msg=""):
        problems.append({"code": code, "axis": axis, "msg": msg})

    def require(code, axis, fn):
        try:
            return fn()
        except RE.EvidenceError as exc:
            bad(code, axis, str(exc))

    if not isinstance(axes, dict):
        bad("STATUS_AXIS_INVALID_STRUCTURE", "ALL", "status record is not an object")
        return problems
    for ax, allowed in ALLOWED.items():
        value = axes.get(ax)
        if not isinstance(value, dict):
            bad("STATUS_AXIS_INVALID_STRUCTURE", ax, "axis must be an object")
        elif not isinstance(value.get("value"), str) or value["value"] not in allowed:
            bad("STATUS_AXIS_INVALID_VALUE", ax, repr(value.get("value")))
    if problems:
        return problems
    A, B, C, D, E = (axes[k] for k in "ABCDE")
    needs_subject = (B.get("value") == "PALI_FIRST_UDOKUMENTOWANY" or C.get("value") in {"PEŁNA_AI", "PEŁNA_AUTOKONTROLA"}
                     or D.get("value") in {"ODSTĄPIONO", "CZĘŚCIOWA", "PEŁNA"}
                     or E.get("value") in ALLOWED["E"] - {"WSTRZYMANE"})
    subject = None
    if needs_subject:
        subject = require("STATUS_SUBJECT_EVIDENCE_INVALID", "ALL", lambda: RE.subject_from(
            evidence, root, subject_id=axes.get("sutta"), revision_id=axes.get("version")))
    ev = evidence if isinstance(evidence, dict) else {}

    def bound(fn):
        if subject is None:
            raise RE.EvidenceError("verified current subject evidence absent")
        return fn()

    if B.get("value") == "PALI_FIRST_UDOKUMENTOWANY":
        require("STATUS_AXIS_B_DOCUMENTED_WITHOUT_R0", "B", lambda: bound(lambda: RE.documented_r0(ev, subject, root, B)))
    if C.get("value") == "PEŁNA_AI":
        if coverage_ready is not True:
            bad("STATUS_AXIS_C_FULL_WITHOUT_COVERAGE", "C")
        require("STATUS_AXIS_C_FULL_WITHOUT_REPORTS", "C", lambda: bound(lambda: RE.full_ai(ev, subject, root)))
    if C.get("value") == "CZĘŚCIOWA":
        require("STATUS_AXIS_C_PARTIAL_WITHOUT_SCOPE", "C", lambda: RE.scope(C.get("scope")))
    if C.get("value") == "PEŁNA_AUTOKONTROLA":
        if coverage_ready is not True:
            bad("STATUS_AXIS_C_FULL_WITHOUT_COVERAGE", "C")
        require("STATUS_AXIS_C_SELF_CHECK_WITHOUT_REPORTS", "C", lambda: bound(lambda: RE.full_author(
            ev, subject, root, contract=author_contract)))
    if D.get("value") == "ODSTĄPIONO":
        require("STATUS_AXIS_D_WAIVER_WITHOUT_DECISION", "D", lambda: bound(lambda: RE.consent(owner, D.get("decision"), "HUMAN_REVIEW_WAIVER", subject, root)))
    if D.get("value") in {"CZĘŚCIOWA", "PEŁNA"}:
        require("STATUS_AXIS_D_HUMAN_WITHOUT_ATTESTATION", "D", lambda: bound(lambda: RE.human_review(ev, subject, root, partial=D["value"] == "CZĘŚCIOWA")))
    if E.get("value") in ALLOWED["E"] - {"WSTRZYMANE"}:
        also = E.get("also", [])
        if not isinstance(also, list) or not all(RE.nonempty(x) for x in also):
            bad("STATUS_AXIS_E_WITHOUT_OWNER_DECISION", "E", "additional decision IDs malformed")
            also = []
        for decision_id in [E.get("decision")] + also:
            require("STATUS_AXIS_E_WITHOUT_OWNER_DECISION", "E", lambda d=decision_id: bound(lambda: RE.consent(owner, d, "PUBLICATION_CONSENT", subject, root)))
        if E["value"] == "DOPUSZCZONE_PO_RECENZJI" and D.get("value") not in {"CZĘŚCIOWA", "PEŁNA"}:
            bad("STATUS_AXIS_E_REVIEW_WITHOUT_REVIEW", "E")
        if B.get("value") == "EN_PL_HH":
            require("STATUS_AXIS_EN_PL_WITHOUT_LICENCE", "E", lambda: bound(lambda: RE.hh_licence(ev, subject, root)))
        if A.get("value") != "UKOŃCZONY_PLIK":
            bad("STATUS_AXIS_E_ON_DRAFT", "E")
    return problems
