# Routing — Opus 5.5 leads, Fable briefs, GPT builds
_Updated 2026-09-23 (GPT-6 Sol + Luna released). Mechanics: [`skills/codex/SKILL.md`](skills/codex/SKILL.md)._

## Who does what
| Seat | Model | Owns |
|---|---|---|
| Flagship / lead | **Opus 5.5** (Claude Code default) | direction, taste gate, secrets, MCP steps, outbound, verification, report |
| Brief writer | **Fable** | the md handoff spec each GPT job builds from; taste calls. No feature code, no forks |
| Hard builder | **`gpt-6-astra`** | design-heavy UI, image-to-code, new systems, pipelines, money-path review |
| Workhorse | **`gpt-6-sol`** | features, fix rounds, refactors, tests-with-code, parallel lanes |
| Grinder | **`gpt-6-luna`** | lint, deps, renames, test sweeps, data/format conversion, log triage |
| Verifier | Sonnet 5 (Agent `model: sonnet`) | re-reviews, log reading, checking a lane's output |
| Lookups | Haiku | trivial reads |

`gpt-5.x` = legacy; don't dispatch. Whatever your `~/.codex/config.toml` default is,
always pass `-m` so the pick is deliberate.

## Picking the GPT model (first match wins)
1. Money path, auth, payments, email, DNS, deploy → **review** with `gpt-6-astra` (`-c model_reasoning_effort=high`).
2. Look matters (site, deck, motion, video components) or it's a new system from scratch → **astra**.
3. Numbered FIXES list with observed symptoms, a feature in an existing pattern, a parallel lane → **sol**.
4. No judgment needed (lint, bump, rename, sweep, convert, summarize logs) → **luna**.
5. Unsure → **sol**. Escalate to astra only after sol misses twice on the same symptom.

Reasoning effort: `medium` default; `high` for reviews and gnarly bugs; `low` for luna grind.
`xhigh`/`max`/`ultra` only when explicitly asked (they burn the cap).

## The handoff (Fable writes, GPT builds, Opus verifies)
1. Fable writes the brief to `<repo>/docs/handoff/<slug>.md` (or the scratchpad) in the
   `codex` skill's spec shape — name files, name skills (`follow $website-build`), quote
   measured symptoms, state caps and "do NOT" lines. The md file IS the prompt.
2. Opus dispatches: `codex exec -m <model> … "$(cat brief.md)" < /dev/null`.
3. Independent pieces → parallel lanes, disjoint file lists, each told what the other owns.
4. Opus verifies (tests, curl, screenshot), runs the review gate, reports back.

## Keep on Claude
Design direction and final taste, secrets, MCP-only tools (Gmail, Slack, Vercel, editors,
paid Higgsfield unless `--approve-for-me`), outbound sends, and nicotine/vape/age-restricted
commerce (GPT refuses at policy level).

## Budget
Astra-only sprints burn the Codex usage cap fast. Sol/Luna exist to carry volume —
don't send grind to astra. Two consecutive usage-limit ERRORs = real cap; fall back to
Opus/Sonnet subagents and tell the human.

## Skill budget (Codex)
Codex fits every skill description into a fixed-size list: 299 skills cut each to ~14 chars,
~145 keeps ~98. Rerun `codex_curate.py` after adding skills; check with `codex debug prompt-input`.
