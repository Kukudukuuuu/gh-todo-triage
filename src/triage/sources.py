"""sources: adapters at the input seam. Both yield Raw issues {id, title, body}."""
from __future__ import annotations

import json
import re

_SECTION = re.compile(r"^###\s+(.+)$", re.M)


def from_gh_json(raw: str) -> list[dict]:
    """Adapter for `gh issue list --json number,title,body` output."""
    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"not JSON: {e}") from e
    if not isinstance(items, list):
        raise ValueError("expected a JSON list of issues")
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        out.append({
            "id": str(it.get("number", it.get("id", "?"))),
            "title": str(it.get("title") or ""),
            "body": str(it.get("body") or ""),
        })
    return out


def from_paste(raw: str) -> list[dict]:
    """Adapter for pasted text: `### Title` sections, else `- title` lines."""
    sections = _SECTION.split(raw)
    if len(sections) >= 3:
        # split keeps [pre, title1, body1, title2, body2, ...]
        out = []
        for i in range(1, len(sections) - 1, 2):
            out.append({"id": f"p{i // 2 + 1}", "title": sections[i].strip(), "body": sections[i + 1].strip()})
        return [o for o in out if o["title"]]
    out = []
    for n, line in enumerate(raw.splitlines(), 1):
        line = line.strip()
        if line.startswith(("- ", "* ")):
            out.append({"id": f"p{n}", "title": line[2:].strip(), "body": ""})
    return out


def load(raw: str) -> list[dict]:
    """Dispatch adapter: gh-JSON list, `###` sections, `- ` lines, or one bare line."""
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("empty input")
    if raw.startswith("["):
        return from_gh_json(raw)
    pasted = from_paste(raw)
    if pasted:
        return pasted
    return [{"id": "p1", "title": raw.splitlines()[0][:120], "body": ""}]
