"""classify: Raw issue -> Verdict. One function is the whole Interface."""
from __future__ import annotations

import re

ROLES = ("needs-triage", "needs-info", "ready-for-agent", "ready-for-human", "wontfix")

_DUP = re.compile(r"duplicat|same as|already (reported|exists|filed)|dup of|#\d+ covers", re.I)
_WONTFIX = re.compile(r"wontfix|won't fix|out of scope|not planned|by design|can'?t reproduce", re.I)
_HUMAN = re.compile(r"\brfc\b|proposal|should we|decide|design doc|decision needed|breaking change|design\b", re.I)
_QUESTION = re.compile(r"\?")
_INFO_WORD = re.compile(r"\b(what|which|version|repro|steps|expected|actual|log|error|stack|trace|os|platform)\b", re.I)
_REPRO = re.compile(r"\b(repro|steps|expected|actual|observed)\b", re.I)


def triage(issue: dict) -> dict:
    """Classify one Raw issue {id, title, body} into {role, reasons}."""
    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    text = f"{title}\n{body}"

    if _DUP.search(text):
        return {"role": "wontfix", "reasons": ["duplicate of an existing issue"]}
    if _WONTFIX.search(text):
        return {"role": "wontfix", "reasons": ["marked out of scope / not planned"]}
    if _HUMAN.search(text):
        return {"role": "ready-for-human", "reasons": ["needs a human decision, not execution"]}
    if _QUESTION.search(title) and _INFO_WORD.search(text):
        return {"role": "needs-info", "reasons": ["asks a question but lacks version/repro detail"]}
    if len(body.strip()) < 20:
        return {"role": "needs-info", "reasons": ["body too short to act on (<20 chars)"]}
    if _REPRO.search(text):
        return {"role": "ready-for-agent", "reasons": ["has repro shape: steps/expected/actual"]}
    if _INFO_WORD.search(text):
        return {"role": "needs-triage", "reasons": ["mentions detail but no clear repro shape"]}
    return {"role": "needs-triage", "reasons": ["no rule fired; needs human eyes first"]}
