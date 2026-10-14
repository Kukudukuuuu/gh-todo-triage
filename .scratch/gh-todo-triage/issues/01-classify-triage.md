# 01: classify module + triage verb

**What to build:** `triage` reads gh-JSON or pasted text, prints one Verdict per issue (role + reasons) in human and `--json` form.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Each of the 5 roles fires on its fixture with a reason
- [ ] `triage --json` parses; paste input yields same Verdicts as gh-JSON input
- [ ] No network calls in code or tests
