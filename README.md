# gh-todo-triage

Raw GitHub issues → agent-ready tickets with blocking edges. Built for the mattpack flow: its tickets feed `/implement` directly.

## Requirements

- Python 3.10+
- `gh` CLI optional (paste text works without it)

## 60-second demo

```bash
python3 -m venv .venv && .venv/bin/pip install typer pytest
export PYTHONPATH=src   # or: .venv/bin/pip install -e .
.venv/bin/python -m pytest -q   # 9 passed

# from live issues
gh issue list --json number,title,body | .venv/bin/python -m triage.cli triage

# or pasted text
printf '### Crash on save\nSteps:\n1. open\n2. save\nExpected ok.\n' \
  | .venv/bin/python -m triage.cli triage
```

Output:

```text
[ready-for-agent] #p1 Crash on save — has repro shape: steps/expected/actual
```

Tickets for the ready set (non-ready issues are counted and skipped):

```bash
gh issue list --json number,title,body \
  | .venv/bin/python -m triage.cli to-tickets --feature login --out-dir out/
# wrote 1 tickets (2 non-ready skipped)  →  out/issues/01-crash.md
```

Each ticket file carries What to build / Blocked by / Status / acceptance checkboxes, numbered blockers-first.

## Roles

| Role | Meaning |
|---|---|
| `ready-for-agent` | repro shape present, grab it |
| `needs-triage` | unclear, human eyes first |
| `needs-info` | too short / question without detail |
| `ready-for-human` | needs a decision, not execution |
| `wontfix` | duplicate or out of scope |

Fix/infra tickets sort first and unblocked (the frontier); feature tickets follow blocked by them; test tickets last, blocked by all.

## Safety

Read-only by default: `triage` prints, `to-tickets` prints unless `--out-dir` is given. No network calls, no GitHub API writes.

## Design

Three deep modules (`codebase-design`): `classify.triage()`, `slice.to_tickets()`, `render.write_markdown()` — one-function interfaces, tests cross them only. Two adapter seams: sources (`gh` JSON vs paste) and writers (markdown now, `--publish` later).
