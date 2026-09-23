# Skill Router — pick the best skill + engine at the start of every task
_Refreshed 2026-09-23 · every skill name verified against an install of 322 · load it from your global `CLAUDE.md` / `AGENTS.md`_

Rule: at the top of any task, match the use-case, invoke the skill, pick the
engine, and say in one line which skill + engine you're using — don't wait to be asked. Two fits → the more
specific/scoped skill wins. Nothing fits → say so and proceed.

Engines (2026-09-23): **Opus 5.5 leads + verifies · Fable writes the md brief ·
GPT builds** — `gpt-6-astra` hard/design, `gpt-6-sol` workhorse, `gpt-6-luna` grind.
All see these skills. Pick rules + handoff: [`ROUTING.md`](ROUTING.md).

## Use-case → engine
| Job | Engine |
|---|---|
| Site / deck / motion / video components, image-to-code, new system | Fable brief → **astra** |
| Feature in an existing pattern, numbered fix round, refactor, parallel lane | Fable brief → **sol** |
| Lint, deps, renames, test sweep, format conversion, log triage | **luna** (Opus writes the one-liner brief) |
| Money / auth / email / DNS / deploy diff | `/codex review` on **astra**, effort high |
| Direction, taste, secrets, MCP, outbound, verification | **Opus 5.5** (stays on Claude) |
| Nicotine / vape / age-restricted commerce | **Opus 5.5** builds (GPT refuses) |
| Verify a lane's output, read logs | Sonnet 5 subagent |

## GPT builders — skills Codex loads (curated to ~145 so descriptions stay readable)
| Builder job | Skill(s) Codex should load |
|---|---|
| Design image → working page | `taste-skill:image-to-code` + one register (`soft-skill` / `minimalist-skill` / `brutalist-skill`) + `impeccable` audit |
| Fix failing CI / address PR review comments | `gh-fix-ci` / `gh-address-comments` |
| Prove it renders (sandbox can't always launch Chromium) | `playwright` / `playwright-interactive` / `screenshot` |
| Money-path or auth review | `security-threat-model` + `security-best-practices` (+ `security-review`) |
| HTML-first video / launch clip | `hyperframes:*` (core, animation, cli, product-launch-video, motion-graphics) or `remotion-*` |
| Next.js / Vercel / AI SDK build | `vercel:nextjs`, `vercel:ai-sdk`, `vercel:vercel-functions`, `vercel:shadcn` |
| Stripe integration | `stripe:stripe-best-practices` |
| Deploy to Render / new CLI tool / ChatGPT app | `render-deploy` / `cli-creator` / `chatgpt-apps` |
| Speech, transcription, notebooks | `speech` / `transcribe` / `jupyter-notebook` (metered OpenAI calls → cost OK first) |
| Keep the diff small | `ponytail:ponytail` / `ponytail:ponytail-review` |
Strategy, marketing, SEO analysis, Vapi, Shippo and n8n skills are switched OFF for Codex
(`scripts/codex_curate.py`) — that work stays with Opus.

## Use-case → skill

| You are doing… | Skill(s) |
|---|---|
| **Process spine** (any build) | `brainstorming` → `writing-plans` → `executing-plans` / `subagent-driven-development` → `verification-before-completion` |
| Keep a build minimal / audit bloat | `ponytail` / `ponytail-review` / `ponytail-audit` |
| Edit real footage (cut/transcribe/grade/subtitle) | `video-use` |
| **HTML-first video** (promo, explainer, captions, slideshow) | `hyperframes` (router) → `product-launch-video` / `faceless-explainer` / `motion-graphics` / `embedded-captions` |
| **AI media generation** (image/video/3D/audio) | `higgsfield-generate` / `higgsfield-product-photoshoot` / `higgsfield-marketplace-cards` — cost-quote first |
| **Programmatic video / launch clip from a site** | `remotion-*` (create/render/captions/studio…), `brag` for a launch video |
| Anti-slop design direction (pick one register) | `taste-core`, `soft-skill` (premium), `minimalist-skill`, `brutalist-skill`, `image-to-code-skill` (board → code) |
| New marketing site or redesign | `website-build` → gate with `taste-core` + `design-motion-principles`; `redesign` for restructure |
| UI motion / animation | `design-motion-principles` + `gsap-*` (core/scrolltrigger/react/timeline…); `frontend-design` for direction |
| Web perf / Core Web Vitals / slow page | `web-perf`, `vercel-optimize` |
| **SEO** (pick the sub-skill) | `seo-technical` / `seo-cluster` / `seo-local` / `seo-schema` / `seo-content` / `seo-geo` / `seo-sitemap` / `seo-sxo` … |
| **Marketing** (pick) | `ads` `cold-email` `prospecting` `pricing` `cro` `copywriting` `emails` `sms` `social` `launch` `referrals` `churn-prevention` `lead-magnets` `ad-creative` `attribution` `analytics` `competitor-profiling` `marketing-council` |
| Charts / dashboards / data viz | `dataviz` |
| Stripe / Shippo | `stripe-best-practices` / `shippo-best-practices` + `label-purchase` `rate-shopping` |
| Email send / templates | `resend` / `resend-cli` / `react-email`; agent inbox → `agent-email-inbox` |
| Supabase / Postgres | `supabase` + `supabase-postgres-best-practices` |
| Vercel deploy / cost | `deploy-to-vercel` / `vercel-cli-with-tokens` / `vercel-optimize` |
| Cloudflare (workers/tunnels/email/turnstile) | `cloudflare` (router) → `workers-best-practices` `wrangler` `durable-objects` `cloudflare-email-service` `turnstile-spin` |
| n8n workflow automation | `n8n-*` (agents/nodes/loops/debugging…) |
| Docs / decks / sheets / PDF | `docs` (living doc), `docx` `pptx` `xlsx` `pdf` |
| **Build an MCP server/app** | `build-mcp-server` / `build-mcp-app` / `build-mcpb` / `mcp-builder` |
| **Diagnose a hard bug / perf regression** | `diagnosing-bugs`; find bugs in a diff → `find-bugs`; review a diff → `code-review` |
| Simplify / clean up code | `code-simplifier`; deepen module design → `codebase-design` / `improve-codebase-architecture` |
| TDD / test-first | `tdd`; pre-commit hooks → `setup-pre-commit` |
| **Security** (repo scan, GHA, settings, skills) | `claude-security` / `gha-security-review` / `claude-settings-audit` / `skill-scanner` |
| PR: open/update/iterate | `pr-writer` / `iterate-pr`; merge conflicts → `resolving-merge-conflicts` |
| Substantial build / refactor / test sweep | `codex` (`-m` astra/sol/luna per engine table) |
| **Author/maintain a skill or command** | `skill-creator` / `skill-writer` / `skill-development` / `command-development` / `hook-development` |
| Improve a CLAUDE.md / AGENTS.md | `claude-md-improver` / `agents-md` |
| **"What automations should this repo have?"** | `claude-automation-recommender` |
| Hand off / continue in background | `claude-handoff` / `handoff` |
| Stress-test a plan or idea | `grilling` / `grill-me` |
| Verify a local web app in a browser | `webapp-testing` / `agent-browser` |
| Prompt tuning | `prompt-optimizer` |
