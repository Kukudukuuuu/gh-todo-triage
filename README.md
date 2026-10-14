# gh-todo-triage

Raw GitHub issues → agent-ready tickets with blocking edges. Built for the mattpack flow: its tickets feed `/implement` directly.

## 60-second demo

```bash
python3 -m venv .venv && .venv/bin/pip install typer pytest
export PYTHONPATH=src
.venv/bin/python -m pytest -q   # 9 passed

# from live issues
gh issue list --json number,title,body | .venv/bin/python -m triage.cli triage

# or pasted text
printf '### Crash on save\nSteps:\n1. open\n2. save\nExpected ok.\n' \
  | .venv/bin/python -m triage.cli triage

# tickets for the ready set
gh issue list --json number,title,body \
  | .venv/bin/python -m triage.cli to-tickets --feature login --out-dir out/
```

## Roles

| Role | Meaning |
|---|---|
| `ready-for-agent` | repro shape present, grab it |
| `needs-triage` | unclear, human eyes first |
| `needs-info` | too short / question without detail |
| `ready-for-human` | needs a decision, not execution |
| `wontfix` | duplicate or out of scope |

`to-tickets` emits `.scratch/<feature>/issues/NN-slug.md` (What / Blocked by / Status / checkboxes), fix tickets first, test tickets last and blocked by all.

## Design

Three deep modules (`codebase-design`): `classify.triage()`, `slice.to_tickets()`, `render.write_markdown()` — one-function interfaces, tests cross them only. Two adapter seams: sources (`gh` JSON vs paste) and writers (markdown now, `--publish` later).
