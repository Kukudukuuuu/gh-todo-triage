"""render: Tickets -> {path: text} markdown files. One function Interface."""
from __future__ import annotations


def write_markdown(tickets: list[dict], feature: str) -> dict[str, str]:
    """Return {relative path: file text}; numbering is blockers-first order."""
    out = {}
    for n, t in enumerate(tickets, 1):
        blocked = ", ".join(t["blocked_by"]) if t["blocked_by"] else "None (can start immediately)"
        criteria = "\n".join(f"- [ ] {c}" for c in t["criteria"])
        out[f".scratch/{feature}/issues/{n:02d}-{t['slug']}.md"] = (
            f"# {n:02d}: {t['title']}\n\n"
            f"**What to build:** {t['what_to_build']}\n\n"
            f"**Blocked by:** {blocked}\n\n"
            f"**Status:** ready-for-agent\n\n{criteria}\n"
        )
    return out
