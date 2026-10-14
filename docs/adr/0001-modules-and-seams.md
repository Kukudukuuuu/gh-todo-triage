# 0001 — Three deep modules, two adapter seams

Date: 2026-10-14
Status: accepted

## Context

Raw GitHub issues arrive unclassified. Turning them into agent-ready tickets is keyword + structure judgement that currently lives in the agent's head each time.

## Decision

Three deep Modules, each with one Interface, tested at that Interface:

- `classify`: `triage(issue) -> Verdict`. Hides keyword rules, dup detection, question detection. Callers learn one function.
- `slice`: `to_tickets(items) -> [Ticket]`. Hides ordering + blocking-edge inference (fix-before-feature, test-after).
- `render`: `write_markdown(tickets, feature) -> {path: text}`. Hides numbering/file template.

Two Seams with Adapters (two adapters = real seam):

- Source seam: gh-JSON adapter vs paste-text adapter, both yield Raw issues.
- Writer seam: markdown writer now; `--publish` (gh issue create) later, same Interface.

## Consequences

- CLI (`triage`, `to-tickets` verbs) is a thin adapter over the three modules.
- No network in tests: hand-made Raw issues cross the same seam as real input.
