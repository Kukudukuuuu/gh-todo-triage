# Glossary — gh-todo-triage

Single-context. Codebase-design terms (Module, Interface, Seam, Adapter, Depth) keep their skill meanings.

- **Raw issue**: unclassified input: `{id, title, body}` from `gh` JSON or pasted text.
- **Verdict**: `{role, reasons[]}`. Role is one of `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
- **Agent-ready**: a Verdict with role `ready-for-agent`: has repro/acceptance shape, no open questions.
- **Ticket**: `{title, what_to_build, blocked_by[], criteria[]}`. `blocked_by` names other ticket titles.
- **Slice**: a vertical tracer-bullet cut; one Ticket covers all layers it touches.
- **Source**: adapter that yields Raw issues (gh CLI adapter, paste adapter).
- **Writer**: adapter that emits Tickets (markdown writer in v1).
