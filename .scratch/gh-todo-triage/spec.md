## Problem Statement

Maintainers drown in raw issues: duplicates, vague reports, feature wishes with no acceptance shape. Deciding what's agent-ready is judgement repeated by hand every time.

## Solution

`triage` CLI: reads Raw issues (`gh issue list --json` or pasted text) → Verdict per issue (role + reasons). `to-tickets`: takes the `ready-for-agent` set → numbered markdown Tickets with blocking edges under `.scratch/<feature>/issues/`.

## User Stories

1. As a maintainer, I want each issue classified into a triage role with reasons, so that I trust the sort.
2. As a maintainer, I want duplicates and info-missing reports flagged, so that agents never grab them.
3. As a maintainer, I want paste input when `gh` isn't available, so that the tool works anywhere.
4. As a maintainer, I want tickets numbered blockers-first with `Blocked by`, so that agents work the frontier.
5. As a maintainer, I want machine JSON out of `triage`, so that scripts can consume it.

## Implementation Decisions

- Modules (codebase-design): `classify.triage(issue)->Verdict`; `slice.to_tickets(items)->[Ticket]`; `render.write_markdown(tickets, feature)->{path: text}`.
- Source seam adapters: gh-JSON (list of `{number,title,body}`) and paste (`### <title>` sections or `- title` lines).
- classify rules: dup (`duplicat|same as|already reported`), needs-info (`?` + `what|which|version|repro|steps|expected|log|error` or body < 20 chars), wontfix (`wontfix|out of scope|not planned|can't reproduce`), ready-for-human (`decide|proposal|rfc|should we|design`), else ready-for-agent when body has repro shape (`repro|steps|expected|actual`), else needs-triage.
- slice edges: infra/fix tickets block feature tickets (title match `fix|setup|infra|refactor|migrate`); test tickets blocked by all (match `test`).
- Writer template: per-ticket file `NN-slug.md` with What/Blocked by/Status/checkboxes.

## Testing Decisions

- Tests cross module Interfaces only, never internals; hand-made Raw issues (no network, no `gh`).
- Good test = literal in, literal out: each rule fires on its fixture; ties prefer the safer role (needs-info over ready-for-agent).
- Prior art: arch-agent-bootstrap CLI-seam tests.

## Out of Scope

- `--publish` to real trackers; LLM classification; multi-repo; auto-closing duplicates.

## Further Notes

- Niche: triage roles match the mattpack flow, so its tickets feed `/implement` directly.
