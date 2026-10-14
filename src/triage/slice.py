"""slice: ready items -> Tickets with blocking edges. One function Interface."""
from __future__ import annotations

import re

_FIX = re.compile(r"\bfix\b|setup|infra|refactor|migrat|chore|ci\b|build", re.I)
_TEST = re.compile(r"\btest\b|tests|coverage|spec\b", re.I)


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return (slug or "ticket")[:40]


def to_tickets(items: list[dict]) -> list[dict]:
    """Order blockers-first; test tickets blocked by all; return Ticket dicts."""
    fixes = [i for i in items if _FIX.search(i["title"])]
    tests = [i for i in items if _TEST.search(i["title"]) and i not in fixes]
    rest = [i for i in items if i not in fixes and i not in tests]
    ordered = fixes + rest + tests
    tickets = []
    fix_titles = [f["title"] for f in fixes]
    for it in ordered:
        if it in fixes:
            blocked: list[str] = []  # fixes are the frontier; they block, they aren't blocked
        elif it in tests:
            blocked = [o["title"] for o in ordered if o is not it and o not in tests]
        else:
            blocked = list(fix_titles)
        tickets.append({
            "title": it["title"],
            "slug": _slug(it["title"]),
            "what_to_build": it.get("body", "")[:500] or it["title"],
            "blocked_by": blocked,
            "criteria": ["done when the behaviour works end-to-end", "covered at the module interface"],
        })
    return tickets
