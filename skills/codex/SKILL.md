---
name: codex
description: Hand a build, refactor, test, or review task to a GPT model via Codex — gpt-6-astra (hard/design builds + money-path review), gpt-6-sol (workhorse features and fix rounds), gpt-6-luna (lint, deps, sweeps, conversions). The rule: Opus 5.5 leads, Fable writes the md brief, GPT builds. Use for any substantial build, mechanical grind, and an adversarial review of every diff touching payments, email, deploys, DNS, or auth. Also on "/codex", "send to codex", "have astra/sol/luna do it". Claude keeps the brief, brand rules, secrets, MCP steps, verification, and the report.
---

# /codex — Opus 5.5 leads, Fable briefs, GPT builds

Usage: `/codex <task>` · `/codex review` (adversarial review of the current diff) · `/codex fix <failing thing>`

## 0. Pick the model (always pass `-m`; full rules in `ROUTING.md`)

| Job | `-m` | effort |
|---|---|---|
| Money/auth/email/DNS/deploy review | `gpt-6-astra` | `high` |
| Look matters (site, deck, motion, video comps), image-to-code, new system | `gpt-6-astra` | `medium` |
| Feature in existing pattern, numbered fix round, refactor, parallel lane | `gpt-6-sol` | `medium` |
| Lint, deps, renames, test sweep, conversion, log triage | `gpt-6-luna` | `low` |

Unsure → sol. Sol misses the same symptom twice → astra. Never `gpt-5.x`.
Effort flag: `-c model_reasoning_effort=<low|medium|high>`; xhigh+ only when explicitly asked.

## 1. Write the brief (the GPT model has no memory of this session)

Fable writes it as an md file (`<repo>/docs/handoff/<slug>.md` or the scratchpad); for a
luna one-liner Opus writes it inline. Self-contained, in this shape:

```
REPO: <abs path>            BRANCH: <name>        DO NOT COMMIT.
GOAL: <one sentence — what "done" looks like>
CONTEXT: <2–5 lines: what exists, entry points, file paths, how it's run/tested>
CONSTRAINTS: <brand palette / no emoji / keep files <500 lines / don't touch X / match existing style>
DELIVER: <files to create or change> + <how to prove it works: test cmd, screenshot, curl>
REPORT: end with a ≤10-line summary: files touched, how you verified, anything unsure.
```

Never put API keys, secret-store contents, or customer data in the prompt.

## 2. Run it

```bash
codex exec -m <model> -c model_reasoning_effort=<effort> -C <repo> -s workspace-write \
  --skip-git-repo-check -o <scratchpad>/codex-last.md "$(cat <brief.md>)" < /dev/null
```

- `< /dev/null` is mandatory — without it codex hangs on "Reading additional input from stdin".
- Timeout 600000; `run_in_background: true` for anything over a minute, then read the file.
- Needs the network (npm install, fetch a URL)? add `-c sandbox_workspace_write.network_access=true`.
- Review: use Codex's native reviewer, not a hand-rolled prompt:
  `cd <repo> && codex review -c model=gpt-6-astra --uncommitted < /dev/null` (astra reviewer; `--base main` for a
  branch). Gotchas: NO `-C` flag — cd first; `--uncommitted`/`--base` CANNOT be combined with a
  custom prompt — a prompt only works as `codex review "<instructions>"` on the whole tree.
- Astra shares Fable's design/build skills — `~/.codex/skills/` symlinks website-build,
  taste-core, design-motion-principles, redesign, video-use, kinetic-type-physics, studio-vfx.
  Name the skill in the spec ("follow the website-build skill") and Astra loads it itself.
- Higgsfield MCP is registered for codex in ~/.codex/config.toml — Astra can generate media itself,
  BUT paid/approval-gated MCP calls are auto-denied under plain `codex exec` ("approval policy is
  never"). For any Higgsfield job use `--approve-for-me` INSTEAD of `-s` (they conflict; it implies
  workspace-write and routes approvals through automatic review). Two gotchas: without it the run
  dies at the first tool call; with it Astra sometimes claims Higgsfield "isn't installed" — put
  "the higgsfield MCP server IS configured; list your MCP tools first" in the spec and it finds them.
- Never `--dangerously-bypass-approvals-and-sandbox`. Never `pkill -f` the codex pattern — kill by PID.

## 3. Verify before reporting (Opus's half)

Read `codex-last.md` (or `~/.codex/handoff/<slug>.md` when the spec named a slug), then
`git -C <repo> diff --stat`. Then actually prove it: run the tests / curl the endpoint /
screenshot the element (headless Chromium). If the diff touches files outside the spec's scope, say so and offer
`git checkout -- <file>`. Do NOT commit on Astra's behalf.

**Review gate**: when `/codex review` comes back with no severity-high findings on a diff
for a money app (anything that charges, pays out, or sends email), record it:
`touch /tmp/astra-review-<pm2-app-name>`. Pair it with a PreToolUse hook that refuses `pm2 restart` of
those apps without a marker under 90 minutes old. Never write the marker without a review.

**Parallel lanes**: independent components → separate `codex exec` runs in background
(`run_in_background: true`, distinct `-o` files and slugs). Opus does MCP/verification
work while they run; never wait idle.

## 4. Report in ≤5 lines, then log the lesson
What changed, how it was verified, anything Astra flagged, what's left for the human.
Then append ONE line to your playbook log (date · task · what
worked/failed · the prompt or flag change that fixes it). Read that file before writing
the next spec.

## When NOT to use
Nicotine/vape/age-restricted commerce (GPT refuses — Opus builds). Design direction, anything that needs Claude's MCP tools (Gmail, Slack, Vercel),
anything reading secrets, and any outbound send — those stay on Claude under your standing rules.
