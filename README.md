<p align="center"><img src="assets/banner.png" alt="Opus 5.5 x GPT New Models Skill Tree — Claude Opus 5.5 leads, GPT-6 Astra, Sol and Luna build" width="100%"></p>

# Opus 5.5 x GPT New Models Skill Tree

**A multi-model routing playbook for Claude Code and OpenAI Codex.** Claude Opus 5.5 is the
flagship lead, Fable writes the markdown handoff briefs, and each build goes to the GPT-6
model that fits the job: **GPT-6 Astra**, **GPT-6 Sol** or **GPT-6 Luna**. It ships **preloaded with 348 skills** (216 included, the rest one command away), a skill
router, a routing table, a `/codex` dispatch skill and an `AGENTS.md` template. Drop
them into `~/.claude` and `~/.codex`, and every agent session will pick the same skill and
model for the same kind of task.

Created by **[Aidan Pierce](https://github.com/AlphaSaleAidan)** · updated 2026-09-23, the day GPT-6 Sol and Luna shipped.

## The routing in one table

| Seat | Model | Does |
|---|---|---|
| Lead | **Claude Opus 5.5** | direction, taste, secrets, MCP tools, verification, the report |
| Brief writer | **Claude Fable** | the self-contained `.md` handoff each GPT job builds from |
| Hard builder | **`gpt-6-astra`** | design-heavy UI, image-to-code, new systems, money-path code review |
| Workhorse | **`gpt-6-sol`** | features, numbered fix rounds, refactors, parallel lanes (default) |
| Grinder | **`gpt-6-luna`** | lint, dependency bumps, renames, test sweeps, format conversion |
| Verifier | Claude Sonnet 5 | re-reviews, log reading, checking a lane's output |

Picking the model: payments/auth/email/DNS/deploy diffs → Astra review at high effort.
The look matters → Astra. Existing pattern or fix list → Sol. No judgment needed → Luna.
Unsure → Sol; escalate to Astra after two misses on the same symptom.

## What's inside

| File | What it is |
|---|---|
| [`SKILL-ROUTER.md`](SKILL-ROUTER.md) | Use-case → engine and use-case → skill decision tables for Claude Code and Codex agents |
| [`ROUTING.md`](ROUTING.md) | Who does what, model-pick rules, reasoning effort, the Fable → GPT → Opus handoff loop |
| [`skills/`](skills/) | 216 ready-to-use skills, each with its upstream license — see the catalog below |
| [`install.sh`](install.sh) | One command: installs all 348 skills for Claude Code and Codex |
| [`scripts/codex_curate.py`](scripts/codex_curate.py) | Gives GPT the builder skills (incl. Claude plugin skills) and switches off strategy/marketing ones — Codex's skill list has a fixed text budget, so ~145 focused skills beat 300 unreadable ones |
| [`skills/codex/SKILL.md`](skills/codex/SKILL.md) | Claude Code skill that dispatches `codex exec -m <model>` with a brief, then verifies |
| [`templates/AGENTS.md`](templates/AGENTS.md) | Standing instructions for the GPT builder (`~/.codex/AGENTS.md`) |

## Install

```bash
git clone https://github.com/AlphaSaleAidan/opus-5-5-x-gpt-skill-tree
cd opus-5-5-x-gpt-skill-tree
./install.sh                                        # all 348 skills → ~/.claude/skills + ~/.agents/skills
cp SKILL-ROUTER.md ROUTING.md ~/.claude/
cp templates/AGENTS.md ~/.codex/AGENTS.md           # review before overwriting your own
npm i -g @openai/codex@latest && codex debug models # confirm gpt-6-sol / gpt-6-luna are listed
```

Then add one line to your global `~/.claude/CLAUDE.md`:
`At the start of every task, route with ~/.claude/SKILL-ROUTER.md and ~/.claude/ROUTING.md.`

## Dispatch example

```bash
codex exec -m gpt-6-sol -c model_reasoning_effort=medium -C ./app -s workspace-write \
  -o /tmp/codex-last.md "$(cat docs/handoff/fix-checkout.md)" < /dev/null
```

`< /dev/null` is required, or `codex exec` waits on stdin.

## Why route this way

- **Cost:** sending lint and dependency bumps to Astra burns the Codex usage cap. Luna and Sol carry that volume.
- **Quality:** the builder never reviews its own work. Opus verifies, and Astra does the adversarial review on money-path diffs.
- **Consistency:** Claude and GPT read the same skill router, so the same task always gets the same skill.

## Skill catalog — 348 skills

**216 are included in [`skills/`](skills/)** (MIT / Apache-2.0, each with its upstream license) and **132 install from their official source** with `./install.sh` (their licenses don't allow redistribution, or they ship as Claude Code plugins). One command gives you the whole tree:

```bash
./install.sh          # copies skills/ into ~/.claude/skills + ~/.agents/skills, then installs the rest
```

<details><summary><b>AgriciDaniel/claude-seo</b> — 30 skills · included</summary>

| Skill | What it does |
|---|---|
| `seo` | Comprehensive SEO analysis for any website or business type. |
| `seo-ahrefs` | Ahrefs API analyst (extension). |
| `seo-backlinks` | Backlink profile analysis: referring domains, anchor text distribution, toxic link detection, competitor gap analysis. |
| `seo-bing` | Bing Webmaster Tools + IndexNow extension. |
| `seo-cluster` | SERP-based semantic topic clustering for content architecture planning. |
| `seo-competitor-pages` | Generate SEO-optimized competitor comparison and alternatives pages. |
| `seo-content` | Content quality and E-E-A-T analysis with AI citation readiness assessment. |
| `seo-content-brief` | Generate competitive SEO content briefs with per-section word counts, competitor scoring, keyword density guidance, a… |
| `seo-dataforseo` | Live SEO data via DataForSEO MCP server. |
| `seo-drift` | SEO drift monitoring: capture baselines of SEO-critical elements, detect changes, and track regressions over time. |
| `seo-ecommerce` | E-commerce SEO analysis: Google Shopping visibility, Amazon marketplace intelligence, product schema validation, comp… |
| `seo-firecrawl` | Full-site crawling, scraping, and site mapping via Firecrawl MCP. |
| `seo-flow` | FLOW framework integration — evidence-led SEO using the Find → Leverage → Optimize → Win loop. |
| `seo-geo` | Optimize content for AI Overviews (formerly SGE), ChatGPT web search, Perplexity, and other AI-powered search experie… |
| `seo-google` | Google SEO APIs: Search Console (Search Analytics, URL Inspection, Sitemaps), PageSpeed Insights v5, CrUX field data … |
| `seo-hreflang` | Hreflang and international SEO audit, validation, and generation. |
| `seo-image-gen` | AI image generation for SEO assets: OG/social preview images, blog hero images, schema images, product photography, i… |
| `seo-images` | Image optimization analysis for SEO and performance. |
| `seo-local` | Local SEO analysis covering Google Business Profile optimization, NAP consistency, citation health, review signals, l… |
| `seo-maps` | Maps intelligence for local SEO — geo-grid rank tracking, GBP profile auditing via API, review intelligence across Go… |
| `seo-page` | Deep single-page SEO analysis covering on-page elements, content quality, technical meta tags, schema, images, and pe… |
| `seo-plan` | Strategic SEO planning for new or existing websites. |
| `seo-profound` | Profound LLM citation tracker (extension). |
| `seo-programmatic` | Programmatic SEO planning and analysis for pages generated at scale from data sources. |
| `seo-schema` | Detect, validate, and generate Schema.org structured data. |
| `seo-seranking` | SE Ranking AI visibility analyst (extension). |
| `seo-sitemap` | Analyze existing XML sitemaps or generate new ones with industry templates. |
| `seo-sxo` | Search Experience Optimization: reads Google SERPs backwards to detect page-type mismatches, derives user stories fro… |
| `seo-technical` | Technical SEO audit across 9 categories: crawlability, indexability, security, URL structure, mobile, Core Web Vitals… |
| `seo-unlighthouse` | Multi-page Lighthouse audit via the MIT-licensed Unlighthouse CLI. |

</details>

<details><summary><b>browser-use/video-use</b> — 1 skills · included</summary>

| Skill | What it does |
|---|---|
| `video-use` | Edit any video by conversation. |

</details>

<details><summary><b>cloudflare/skills</b> — 8 skills · included</summary>

| Skill | What it does |
|---|---|
| `agents-sdk` | Build, debug, or review Cloudflare Agents SDK applications using the agents package. |
| `cloudflare` | Discover and choose Cloudflare products for apps, APIs, AI agents, storage, networking, and security. |
| `cloudflare-email-service` | Implement or troubleshoot Cloudflare Email Sending and Email Routing integrations and their delivery configuration. |
| `durable-objects` | Build, debug, or review Cloudflare Durable Objects code for persistent state and coordination. |
| `turnstile-spin` | Set up, repair, or migrate to Cloudflare Turnstile bot verification in an existing frontend and backend, including se… |
| `web-perf` | Audit, diagnose, or optimize website loading and interaction performance, Core Web Vitals, and Lighthouse performance… |
| `workers-best-practices` | Cloudflare Workers best practices for production applications. |
| `wrangler` | Run or troubleshoot Wrangler CLI commands and configure Worker projects for local development, deployment, and Cloudf… |

</details>

<details><summary><b>coreyhaines31/marketingskills</b> — 34 skills · included</summary>

| Skill | What it does |
|---|---|
| `ab-testing` | When the user wants to plan, design, or implement an A/B test or experiment, or build a growth experimentation progra… |
| `ad-creative` | When the user wants to generate, iterate, or scale ad creative — headlines, descriptions, primary text, or full ad va… |
| `ads` | When the user wants help with paid advertising campaigns on Google Ads, Meta (Facebook/Instagram), LinkedIn, Twitter/… |
| `analytics` | When the user wants to set up, improve, or audit analytics tracking and measurement. |
| `attribution` | When the user wants to figure out which marketing actually drives conversions and revenue, choose or interpret an att… |
| `churn-prevention` | When the user wants to reduce churn, build cancellation flows, set up save offers, recover failed payments, or implem… |
| `cold-email` | Write B2B cold emails and follow-up sequences that get replies. |
| `competitor-profiling` | When the user wants to research, profile, or analyze competitors from their URLs. |
| `content-strategy` | When the user wants to plan a content strategy, decide what content to create, or figure out what topics to cover. |
| `copy-editing` | When the user wants to edit, review, or improve existing marketing copy, or refresh outdated content. |
| `copywriting` | When the user wants to write, rewrite, or improve marketing copy for any page — including homepage, landing pages, pr… |
| `cro` | When the user wants to optimize, improve, or increase conversions on any marketing page or form — including homepage,… |
| `customer-research` | When the user wants to conduct, analyze, or synthesize customer research. |
| `emails` | When the user wants to create or optimize an email sequence, drip campaign, automated email flow, or lifecycle email … |
| `launch` | When the user wants to plan a product launch, feature announcement, or release strategy. |
| `lead-magnets` | When the user wants to create, plan, or optimize a lead magnet for email capture or lead generation. |
| `marketing-council` | When the user wants multiple expert perspectives on a marketing question — a simulated board of advisors staffed by l… |
| `marketing-ideas` | When the user needs marketing ideas, inspiration, or strategies for their SaaS or software product. |
| `marketing-loops` | When the user wants to set up a recurring, self-running marketing workflow — a repeatable loop an AI agent runs on a … |
| `marketing-plan` | When the user needs a comprehensive marketing plan for a client, a company they advise, or their own product. |
| `marketing-psychology` | When the user wants to apply psychological principles, mental models, or behavioral science to marketing. |
| `offers` | When the user wants to design, construct, or improve an offer — the thing they actually sell — including value framin… |
| `onboarding` | When the user wants to optimize post-signup onboarding, user activation, first-run experience, or time-to-value. |
| `paywalls` | When the user wants to create or optimize in-app paywalls, upgrade screens, upsell modals, or feature gates. |
| `popups` | When the user wants to create or optimize popups, modals, overlays, slide-ins, or banners for conversion purposes. |
| `pricing` | When the user wants help with pricing decisions, packaging, or monetization strategy. |
| `product-marketing` | When the user wants to create or update their product marketing context document. |
| `prospecting` | When the user wants to find, qualify, and build a list of prospects to reach out to — across B2B SaaS, general B2B, o… |
| `referrals` | When the user wants to create, optimize, or analyze a referral program, affiliate program, or word-of-mouth strategy. |
| `revops` | When the user wants help with revenue operations, lead lifecycle management, or marketing-to-sales handoff processes. |
| `sales-enablement` | When the user wants to create sales collateral, pitch decks, one-pagers, objection handling docs, or demo scripts. |
| `signup` | When the user wants to optimize signup, registration, account creation, or trial activation flows. |
| `sms` | When the user wants to plan, build, or optimize SMS or MMS marketing — including welcome flows, abandoned cart texts,… |
| `social` | When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram,… |

</details>

<details><summary><b>getsentry/skills</b> — 12 skills · included</summary>

| Skill | What it does |
|---|---|
| `agents-md` | Creates and maintains concise AGENTS.md and CLAUDE.md project instruction files. |
| `claude-settings-audit` | Analyze a repository to generate recommended Claude Code settings.json permissions. |
| `code-simplifier` | Simplifies and refines code for clarity, consistency, and maintainability while preserving all functionality. |
| `doc-coauthoring` | Guide users through a structured workflow for co-authoring documentation. |
| `find-bugs` | Find bugs, security vulnerabilities, and code quality issues in local branch changes. |
| `gha-security-review` | GitHub Actions security review for workflow exploitation vulnerabilities. |
| `iterate-pr` | Iterate on a PR until actionable CI passes and high/medium review feedback is addressed. |
| `pr-writer` | Create or refresh reviewer-facing PR titles and descriptions. |
| `prompt-optimizer` | Creates, optimizes, and iteratively refines agent prompts, system prompts, developer prompts, and reusable prompt tem… |
| `security-review` | Security code review for vulnerabilities. |
| `skill-scanner` | Scan agent skills for security issues. |
| `skill-writer` | Create, synthesize, and iteratively improve agent skills following the Agent Skills specification. |

</details>

<details><summary><b>greensock/gsap-skills</b> — 8 skills · included</summary>

| Skill | What it does |
|---|---|
| `gsap-core` | Official GSAP skill for the core API — gsap.to(), from(), fromTo(), easing, duration, stagger, defaults, gsap.matchMe… |
| `gsap-frameworks` | Official GSAP skill for Vue, Svelte, and other non-React frameworks — lifecycle, scoping selectors, cleanup on unmoun… |
| `gsap-performance` | Official GSAP skill for performance — prefer transforms, avoid layout thrashing, will-change, batching. |
| `gsap-plugins` | Official GSAP skill for GSAP plugins — registration, ScrollToPlugin, ScrollSmoother, Flip, Draggable, Inertia, Observ… |
| `gsap-react` | Official GSAP skill for React — useGSAP hook, refs, gsap.context(), cleanup. |
| `gsap-scrolltrigger` | Official GSAP skill for ScrollTrigger — scroll-linked animations, pinning, scrub, triggers. |
| `gsap-timeline` | Official GSAP skill for timelines — gsap.timeline(), position parameter, nesting, playback. |
| `gsap-utils` | Official GSAP skill for gsap.utils — clamp, mapRange, normalize, interpolate, random, snap, toArray, wrap, pipe. |

</details>

<details><summary><b>higgsfield-ai/skills</b> — 4 skills · included</summary>

| Skill | What it does |
|---|---|
| `higgsfield-generate` | Generate images/videos/3D assets/audio via Higgsfield AI. |
| `higgsfield-marketplace-cards` | Generate marketplace product image cards through Higgsfield: compliant main image, secondary product images, and A+ s… |
| `higgsfield-product-photoshoot` | Generate brand-quality product images through Higgsfield product-photoshoot prompt enhancement on GPT Image 2 / gpt_i… |
| `higgsfield-soul-id` | Train a Soul Character — a personalized model on a person's face that Higgsfield uses for identity-faithful image and… |

</details>

<details><summary><b>kylezantos/design-motion-principles</b> — 1 skills · included</summary>

| Skill | What it does |
|---|---|
| `design-motion-principles` | Motion and interaction design expert based on Emil Kowalski, Jakub Krehel, and Jhey Tompkins' techniques. |

</details>

<details><summary><b>latent-spaces/brag</b> — 1 skills · included</summary>

| Skill | What it does |
|---|---|
| `brag` | Turn the current project website into a short, polished, shareable launch video using Hyperframes. |

</details>

<details><summary><b>Leonxlnx/taste-skill</b> — 15 skills · included</summary>

| Skill | What it does |
|---|---|
| `brandkit` | Premium brand-kit image generation skill for creating high-end brand-guidelines boards, logo systems, identity decks,… |
| `brutalist-skill` | Raw mechanical interfaces fusing Swiss typographic print with military terminal aesthetics. |
| `gpt-tasteskill` | Elite UX/UI & Advanced GSAP Motion Engineer. |
| `image-to-code-skill` | Elite website image-to-code skill for Codex. |
| `imagegen-frontend-mobile` | Elite mobile app image-generation skill for creating premium, app-native screen concepts and flows. |
| `imagegen-frontend-web` | Elite frontend image-direction skill for generating premium, conversion-aware website design references. |
| `minimalist-skill` | Clean editorial-style interfaces. |
| `output-skill` | Overrides default LLM truncation behavior. |
| `redesign` | Upgrades existing websites and apps to premium quality. |
| `redesign-skill` | Upgrades existing websites and apps to premium quality. |
| `soft-skill` | Teaches the AI to design like a high-end agency. |
| `stitch-skill` | Semantic Design System Skill for Google Stitch. |
| `taste-core` | Anti-slop frontend skill for landing pages, portfolios, and redesigns. |
| `taste-skill` | Anti-slop frontend skill for landing pages, portfolios, and redesigns. |
| `taste-skill-v1` | The original v1 taste-skill, preserved for projects depending on its exact behavior. |

</details>

<details><summary><b>mattpocock/skills</b> — 25 skills · included</summary>

| Skill | What it does |
|---|---|
| `claude-handoff` | Hand the current conversation off to a fresh background agent that picks up the work immediately. |
| `code-review` | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code … |
| `codebase-design` | Shared vocabulary for designing deep modules. |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions. |
| `domain-modeling` | Build and sharpen a project's domain model. |
| `git-guardrails-claude-code` | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they exe… |
| `grill-me` | A relentless interview to sharpen a plan or design. |
| `grill-with-docs` | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. |
| `grilling` | Grill the user relentlessly about a plan, decision, or idea. |
| `handoff` | Compact the current conversation into a handoff document for another agent to pick up. |
| `implement` | Implement a piece of work based on a spec or set of tickets. |
| `implement-spec` | Implement a specification in code. |
| `improve-codebase-architecture` | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one y… |
| `prototype` | Build a throwaway prototype to answer a design question. |
| `research` | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. |
| `resolving-merge-conflicts` | Use when you need to resolve an in-progress git merge/rebase conflict. |
| `setup-pre-commit` | Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. |
| `tdd` | Test-driven development. |
| `to-questionnaire` | Turn a decision you can't fully answer into a questionnaire for someone else to fill in. |
| `to-spec` | Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis o… |
| `to-tickets` | Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edge… |
| `triage` | Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write … |
| `wayfinder` | Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tr… |
| `wizard` | Generate an interactive bash wizard that walks a human through steps only they can perform. |
| `writing-for-agents` | Writing documents for agents. |

</details>

<details><summary><b>n8n-io/skills</b> — 14 skills · included</summary>

| Skill | What it does |
|---|---|
| `n8n-agents-official` | Use when building or editing any AI feature in n8n: AI Agents, Text Classifier, Information Extractor, Sentiment Anal… |
| `n8n-binary-and-data-official` | Use when handling files, images, attachments, or binary data in n8n, OR when an AI agent needs to take a user-uploade… |
| `n8n-code-nodes-official` | Use when the user reaches for a Code node, mentions writing JavaScript or Python in n8n, or any custom logic comes up… |
| `n8n-credentials-and-security-official` | Use when handling any auth, API keys, tokens, OAuth, bearer tokens, basic auth, or secret values in n8n workflows. |
| `n8n-data-tables-official` | Use when working with n8n's built-in Data Tables, designing schemas, inserting/updating/upserting rows, deduping, or … |
| `n8n-debugging-official` | Use when an n8n workflow isn't working, errors appear, results don't match what was expected, or the user says "this … |
| `n8n-error-handling-official` | Use when building any webhook-triggered workflow, scheduled/production-bound workflow, wiring a per-node error output… |
| `n8n-expressions-official` | Use when writing or reviewing n8n expressions (`{{...}}` syntax), `$json` / `$node` references, Luxon date code, or e… |
| `n8n-extending-mcp-official` | Use when you want to expose an n8n workflow as a tool the coding agent can call. |
| `n8n-loops-official` | Use when working with multi-item data, batches, paginated APIs, rate-limited APIs, fan-out across multiple branches, … |
| `n8n-node-configuration-official` | Use when configuring any n8n node: HTTP, webhooks, database, comms (Slack/Gmail/Discord), AI, triggers, Merge, anythi… |
| `n8n-subworkflows-official` | Use when building anything multi-step, anything that looks repeatable, anything the user mentions reusing, or any wor… |
| `n8n-workflow-lifecycle-official` | Use when starting, designing, organizing, finishing, or shipping an n8n workflow. |
| `using-n8n-skills-official` | Use when working with n8n workflows in any capacity. |

</details>

<details><summary><b>obra/superpowers</b> — 14 skills · included</summary>

| Skill | What it does |
|---|---|
| `brainstorming` | You MUST use this before any creative work - creating features, building components, adding functionality, or modifyi… |
| `dispatching-parallel-agents` | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| `executing-plans` | Use when you have a written implementation plan to execute in a separate session with review checkpoints |
| `finishing-a-development-branch` | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work |
| `receiving-code-review` | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or tec… |
| `requesting-code-review` | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `subagent-driven-development` | Use when executing implementation plans with independent tasks in the current session |
| `systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `test-driven-development` | Use when implementing any feature or bugfix, before writing implementation code |
| `using-git-worktrees` | Use when starting feature work that needs isolation from current workspace or before executing implementation plans -… |
| `using-superpowers` | Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY re… |
| `verification-before-completion` | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running ver… |
| `writing-plans` | Use when you have a spec or requirements for a multi-step task, before touching code |
| `writing-skills` | Use when creating new skills, editing existing skills, or verifying skills work before deployment |

</details>

<details><summary><b>pbakaus/impeccable</b> — 1 skills · included</summary>

| Skill | What it does |
|---|---|
| `impeccable` | Design-quality audit and polish for frontend UI — catches generic AI-looking patterns and fixes them. |

</details>

<details><summary><b>resend/resend-skills</b> — 5 skills · included</summary>

| Skill | What it does |
|---|---|
| `agent-email-inbox` | Use when building any system where email content triggers actions — AI agent inboxes, automated support handlers, ema… |
| `email-best-practices` | Use when building email features, emails going to spam, high bounce rates, setting up SPF/DKIM/DMARC authentication, … |
| `react-email` | Use when building HTML email templates with React components, adding a visual email editor to an application using th… |
| `resend` | Use when working with the Resend email API — sending transactional emails (single or batch), receiving inbound emails… |
| `resend-cli` | Operate the Resend platform from the terminal — send emails (including React Email .tsx templates via --react-email),… |

</details>

<details><summary><b>ruvnet/claude-flow</b> — 39 skills · included</summary>

| Skill | What it does |
|---|---|
| `agentdb-advanced` | Master advanced AgentDB features including QUIC synchronization, multi-database management, custom distance metrics, … |
| `agentdb-learning` | Create and train AI learning plugins with AgentDB's 9 reinforcement learning algorithms. |
| `agentdb-memory-patterns` | Implement persistent memory patterns for AI agents using AgentDB. |
| `agentdb-optimization` | Optimize AgentDB performance with quantization (4-32x memory reduction), HNSW indexing (150x faster search), caching,… |
| `agentdb-vector-search` | Implement semantic vector search with AgentDB for intelligent document retrieval, similarity matching, and context-aw… |
| `agentic-jujutsu` | Quantum-resistant, self-learning version control for AI agents with ReasoningBank intelligence and multi-agent coordi… |
| `browser` | Web browser automation with AI-optimized snapshots for claude-flow agents |
| `dual-mode` | Run Claude Code and OpenAI Codex together on one task — Claude designs and reviews, Codex implements. |
| `flow-nexus-neural` | Train and deploy neural networks in distributed E2B sandboxes with Flow Nexus |
| `flow-nexus-platform` | Comprehensive Flow Nexus platform management - authentication, sandboxes, app deployment, payments, and challenges |
| `flow-nexus-swarm` | Cloud-based AI swarm deployment and event-driven workflow automation with Flow Nexus platform |
| `github-code-review` | Comprehensive GitHub code review with AI-powered swarm coordination |
| `github-multi-repo` | Multi-repository coordination, synchronization, and architecture management with AI swarm orchestration |
| `github-project-management` | Comprehensive GitHub project management with swarm-coordinated issue tracking, project board automation, and sprint p… |
| `github-release-management` | Comprehensive GitHub release orchestration with AI swarm coordination for automated versioning, testing, deployment, … |
| `github-workflow-automation` | Advanced GitHub Actions workflow automation with AI swarm coordination, intelligent CI/CD pipelines, and comprehensiv… |
| `hive-mind-advanced` | Advanced Hive Mind collective intelligence system for queen-led multi-agent coordination with consensus mechanisms an… |
| `hooks-automation` | Automated coordination, formatting, and learning from Claude Code operations using intelligent hooks with MCP integra… |
| `pair-programming` | AI-assisted pair programming with multiple modes (driver/navigator/switch), real-time verification, quality monitorin… |
| `performance-analysis` | Comprehensive performance analysis, bottleneck detection, and optimization recommendations for Claude Flow swarms |
| `reasoningbank-agentdb` | Implement ReasoningBank adaptive learning with AgentDB's 150x faster vector database. |
| `reasoningbank-intelligence` | Implement adaptive learning with ReasoningBank for pattern recognition, strategy optimization, and continuous improve… |
| `skill-builder` | Create new Claude Code Skills with proper YAML frontmatter, progressive disclosure structure, and complete directory … |
| `sparc-methodology` | SPARC (Specification, Pseudocode, Architecture, Refinement, Completion) comprehensive development methodology with mu… |
| `stream-chain` | Stream-JSON chaining for multi-agent pipelines, data transformation, and sequential workflows |
| `swarm-advanced` | Advanced swarm orchestration patterns for research, development, testing, and complex distributed workflows |
| `swarm-orchestration` | Orchestrate multi-agent swarms with agentic-flow for parallel task execution, dynamic topology, and intelligent coord… |
| `v3-cli-modernization` | CLI modernization and hooks system enhancement for claude-flow v3. |
| `v3-core-implementation` | Core module implementation for claude-flow v3. |
| `v3-ddd-architecture` | Domain-Driven Design architecture for claude-flow v3. |
| `v3-integration-deep` | Deep agentic-flow@alpha integration implementing ADR-001. |
| `v3-mcp-optimization` | MCP server optimization and transport layer enhancement for claude-flow v3. |
| `v3-memory-unification` | Unify 6+ memory systems into AgentDB with HNSW indexing for 150x-12,500x search improvements. |
| `v3-performance-optimization` | Achieve aggressive v3 performance targets: 2.49x-7.47x Flash Attention speedup, 150x-12,500x search improvements, 50-… |
| `v3-security-overhaul` | Complete security architecture overhaul for claude-flow v3. |
| `v3-swarm-coordination` | 15-agent hierarchical mesh coordination for v3 implementation. |
| `verification-quality` | Comprehensive truth scoring, code quality verification, and automatic rollback system with 0.95 accuracy threshold fo… |
| `worker-benchmarks` | Run comprehensive worker system benchmarks and performance analysis |
| `worker-integration` | Worker-Agent integration for intelligent task dispatch and performance tracking |

</details>

<details><summary><b>supabase/agent-skills</b> — 2 skills · included</summary>

| Skill | What it does |
|---|---|
| `supabase` | Use when doing ANY task involving Supabase. |
| `supabase-postgres-best-practices` | Postgres best practices maintained by Supabase, for Postgres running anywhere. |

</details>

<details><summary><b>this repo (Aidan Pierce)</b> — 1 skills · included</summary>

| Skill | What it does |
|---|---|
| `codex` | Hand a build, refactor, test, or review task to a GPT model via Codex — gpt-6-astra (hard/design builds + money-path … |

</details>

<details><summary><b>vercel-labs/agent-browser</b> — 1 skills · included</summary>

| Skill | What it does |
|---|---|
| `agent-browser` | Browser automation CLI for AI agents. |

</details>

<details><summary><b>anthropics/skills</b> — 3 skills · installs from source</summary>

| Skill | What it does |
|---|---|
| `frontend-design` | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. |
| `skill-creator` | Create new skills, modify and improve existing skills, and measure skill performance. |
| `webapp-testing` | Toolkit for interacting with and testing local web applications using Playwright. |

</details>

<details><summary><b>claude-md-management@claude-plugins-official</b> — 1 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `claude-md-improver` | Audit and improve CLAUDE.md files in repositories. |

</details>

<details><summary><b>hookify@claude-plugins-official</b> — 1 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `writing-rules` | This skill should be used when the user asks to "create a hookify rule", "write a hook rule", "configure hookify", "a… |

</details>

<details><summary><b>hyperframes@claude-plugins-official</b> — 26 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `captions-overlay` | Overlay doctrine for the embedded-captions workflow — the caption MODEL (drop / rail / embed) and the rule that capti… |
| `changelog-video` | Turn a weekly changelog .md into a finished branded changelog video (square 1080, ~45-60s, Annie VO, animated brand b… |
| `cut-the-curve` | The technique catalog: five velocity-matched SEAMS (zoom-through, INVERSE zoom-through, cut-the-curve, waterfall cut,… |
| `embedded-captions` | Add captions or subtitles to an existing single-subject talking-head video without editing the footage. |
| `faceless-explainer` | Turn arbitrary text — an article, notes, a topic, a brief — into a faceless explainer video: there is no site or foot… |
| `figma` | Import Figma content into a HyperFrames composition — rendered assets, brand tokens, components, storyboard sections … |
| `general-video` | Author or edit a custom HyperFrames composition when no specialized workflow fits, or when BRIEF.md sets flow: compan… |
| `hyperframes` | Mandatory entry point: read this first for any request to make, create, edit, animate, or render a video, animation, … |
| `hyperframes-animation` | All animation knowledge for HyperFrames — atomic motion rules, multi-phase scene blueprints, scene transitions, broad… |
| `hyperframes-audio` | Use when audio already placed in a HyperFrames composition needs to be mixed: fade-in/fade-out, crossfade, track gain… |
| `hyperframes-cli` | Use the HyperFrames CLI development loop: init, add, catalog, capture, lint, check, snapshot, compare, grade-compare,… |
| `hyperframes-core` | The HyperFrames composition contract — build one renderable project. |
| `hyperframes-creative` | Non-animation creative direction for HyperFrames videos. |
| `hyperframes-keyframes` | Use when a HyperFrames composition needs a punch-in, punch-out, zoom, reframe, Ken Burns treatment, camera move, visu… |
| `hyperframes-registry` | Install, discover, and wire registry blocks and components into HyperFrames compositions. |
| `media-use` | Agent Media OS, the single skill for every media need in a HyperFrames project. |
| `motion-doctrine` | GATEWAY — load FIRST before composing any HyperFrames animation or video. |
| `motion-graphics` | A short, design-led motion graphic where motion is the message — kinetic typography, stat count-up, chart/data-viz hi… |
| `music-to-video` | Turn a music track (an audio file, a video to pull audio from, or a track generated from a mood brief) into a beat-sy… |
| `oversized-cursor` | House-style oversized macOS cursor technique for HyperFrames launch videos. |
| `pr-to-video` | Turn a GitHub pull request (a PR URL, owner/repo#N, or 'this PR' in a checked-out repo) into a code-change explainer … |
| `product-launch-video` | Turn a product or marketing URL, pasted script, or brief into a product launch / promo video — SaaS promos, feature r… |
| `remotion-to-hyperframes` | Port an existing Remotion (React) composition''s source to HyperFrames HTML. |
| `seam-craft` | Render-correctness doctrine for scene-to-scene seams in HyperFrames launch videos — the prerequisites that make trans… |
| `slideshow` | Author a HyperFrames slideshow — a presentation, pitch deck, or interactive deck with discrete slides, fragment revea… |
| `talking-head-recut` | Package an existing talking-head / interview / podcast video with timed, designed GRAPHIC OVERLAY cards — kinetic tit… |

</details>

<details><summary><b>openai/skills (Codex)</b> — 15 skills · installs from source</summary>

| Skill | What it does |
|---|---|
| `chatgpt-apps` | Build, scaffold, refactor, and troubleshoot ChatGPT Apps SDK applications that combine an MCP server and widget UI. |
| `cli-creator` | Build a composable CLI for Codex from API docs, an OpenAPI spec, existing curl examples, an SDK, a web app, an admin … |
| `define-goal` | Help the user define a concrete, measurable goal before starting work, especially when they ask to use the goal tool,… |
| `gh-address-comments` | Help address review/issue comments on the open GitHub PR for the current branch using gh CLI; verify gh auth first an… |
| `gh-fix-ci` | Use when a user asks to debug or fix failing GitHub PR checks that run in GitHub Actions; use `gh` to inspect checks … |
| `jupyter-notebook` | Use when the user asks to create, scaffold, or edit Jupyter notebooks (`.ipynb`) for experiments, explorations, or tu… |
| `playwright` | Use when the task requires automating a real browser from the terminal (navigation, form filling, snapshots, screensh… |
| `playwright-interactive` | Persistent browser and Electron interaction through `js_repl` for fast iterative UI debugging. |
| `render-deploy` | Deploy applications to Render by analyzing codebases, generating render.yaml Blueprints, and providing Dashboard deep… |
| `screenshot` | Use when the user explicitly asks for a desktop or system screenshot (full screen, specific app or window, or a pixel… |
| `security-best-practices` | Perform language and framework specific security best-practice reviews and suggest improvements. |
| `security-ownership-map` | Analyze git repositories to build a security ownership topology (people-to-file), compute bus factor and sensitive-co… |
| `security-threat-model` | Repository-grounded threat modeling that enumerates trust boundaries, assets, attacker capabilities, abuse paths, and… |
| `speech` | Use when the user asks for text-to-speech narration or voiceover, accessibility reads, audio prompts, or batch speech… |
| `transcribe` | Transcribe audio files to text with optional diarization and known-speaker hints. |

</details>

<details><summary><b>ponytail (claude.ai plugin directory)</b> — 6 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `ponytail` | Forces the laziest solution that actually works, simplest, shortest, most minimal. |
| `ponytail-audit` | Whole-repo audit for over-engineering. |
| `ponytail-debt` | Harvest every `ponytail:` comment in the codebase into a debt ledger, so the deliberate shortcuts and deferrals ponyt… |
| `ponytail-gain` | Show ponytail's measured impact as a compact scoreboard: less code, less cost, more speed, from the benchmark medians. |
| `ponytail-help` | Quick-reference card for all ponytail modes, skills, and commands. |
| `ponytail-review` | Code review focused exclusively on over-engineering. |

</details>

<details><summary><b>remotion-dev/skills</b> — 12 skills · installs from source</summary>

| Skill | What it does |
|---|---|
| `remotion-best-practices` | Router for all Remotion skills |
| `remotion-captions` | Transcribing, displaying and animating captions |
| `remotion-create` | Create a new Remotion video |
| `remotion-docs` | Search Remotion documentation |
| `remotion-interactivity` | Structure Remotion markup for interactivity |
| `remotion-maps` | Remotion Map animation knowledge |
| `remotion-markup` | Content, animation and effects best practices |
| `remotion-multimedia` | Interacting with Mediabunny |
| `remotion-render` | Export a Remotion video |
| `remotion-saas` | Build an app with Remotion |
| `remotion-studio` | Preview a Remotion video |
| `remotion-upgrade` | Upgrade Remotion, and related packages |

</details>

<details><summary><b>session-report@claude-plugins-official</b> — 1 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `session-report` | Generate an explorable HTML report of Claude Code session usage (tokens, cache, subagents, skills, expensive prompts)… |

</details>

<details><summary><b>shippo@claude-plugins-official</b> — 9 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `address-validation` | Validate, parse, and standardize shipping addresses via the Shippo API |
| `batch-shipping` | Process bulk shipments from CSV files, create and purchase batch labels, and generate end-of-day manifests via the Sh… |
| `label-purchase` | Purchase domestic and international shipping labels, handle customs declarations, return labels, and void/refund labe… |
| `rate-shopping` | Compare multi-carrier shipping rates, find cheapest/fastest options, and get shipping recommendations via the Shippo … |
| `shipping-analysis` | Analyze shipping costs, compare carriers, optimize package dimensions, and review historical shipping spend via the S… |
| `shippo-best-practices` | - Guides Shippo integration decisions, choosing between Rates at Checkout vs. |
| `shippo-support-ticket` | Generate a complete, auto-classified, ready-to-paste Shippo support ticket for a single shipment or label. |
| `tracking` | Track packages across carriers, view tracking history, and set up tracking webhooks via the Shippo API |
| `upgrade-shippo` | - Guide for Shippo API version changes, webhook payload versioning, and how the hosted MCP server handles updates. |

</details>

<details><summary><b>stripe@claude-plugins-official</b> — 3 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `stripe-best-practices` | - Guides Stripe integration decisions — API selection (Checkout Sessions vs PaymentIntents), Connect platform setup (… |
| `stripe-projects` | - Use when setting up a new app or local repo with Stripe Projects, provisioning a software stack, or bootstrapping t… |
| `upgrade-stripe` | Guide for upgrading Stripe API versions and SDKs |

</details>

<details><summary><b>vapi-voice-ai@vapi-skills</b> — 12 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `create-assistant` | Design, create, or validate saved and transient Vapi voice assistants. |
| `create-call` | Create one-off outbound phone calls, web calls, scheduled calls, and simple batch calls using the Vapi API. |
| `create-campaign` | Create, schedule, duplicate, inspect, cancel, archive, and troubleshoot Vapi outbound Campaigns. |
| `create-phone-number` | Plan, provision, import, route, update, and verify Vapi phone numbers through the public API. |
| `create-squad` | Design, create, update, and verify Vapi Squads and documented handoff tools through the public API. |
| `create-structured-output` | Design, create, inspect, update, attach, detach, preview, execute, and verify reusable Vapi Structured Outputs throug… |
| `create-tool` | Select, define, create, inspect, update, attach, detach, and verify reusable Vapi tools through the public API. |
| `setup-api-key` | Guide users through obtaining and configuring a Vapi API key. |
| `setup-webhook` | Configure Vapi server URLs and webhooks to receive real-time call events, transcripts, tool calls, and end-of-call re… |
| `simulations` | Design, create, run, monitor, and maintain Vapi Simulations for assistants and squads. |
| `vapi-bootstrap-framework` | Opt-in recreation of the Bun + TypeScript framework used to build Vapi's landing-page voice agents from a ROUGH_DRAFT… |
| `vapi-prompt-builder` | Create, improve, or audit Vapi voice agent and Squad system prompts for production phone and web based voice agents. |

</details>

<details><summary><b>vercel-labs/agent-skills</b> — 9 skills · installs from source</summary>

| Skill | What it does |
|---|---|
| `deploy-to-vercel` | Deploy applications and websites to Vercel. |
| `vercel-cli-with-tokens` | Deploy and manage projects on Vercel using token-based authentication. |
| `vercel-composition-patterns` | React composition patterns that scale. |
| `vercel-optimize` | Use for Vercel cost and performance optimization on deployed projects, especially Next.js, SvelteKit, Nuxt, and limit… |
| `vercel-react-best-practices` | React and Next.js performance optimization guidelines from Vercel Engineering. |
| `vercel-react-native-skills` | React Native and Expo best practices from Vercel. |
| `vercel-react-view-transitions` | Guide for implementing smooth, native-feeling animations using React's View Transition API (`<ViewTransition>` compon… |
| `web-design-guidelines` | Review UI code for Web Interface Guidelines compliance. |
| `writing-guidelines` | Vercel writing guidelines for clear, consistent technical prose. |

</details>

<details><summary><b>vercel@claude-plugins-official</b> — 33 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `ai-gateway` | Vercel AI Gateway expert guidance. |
| `ai-sdk` | Vercel AI SDK expert guidance. |
| `auth` | Authentication integration guidance — Clerk (native Vercel Marketplace), Descope, and Auth0 setup for Next.js applica… |
| `benchmark-agents` | Advanced AI agent benchmark scenarios that push Vercel's cutting-edge platform features — Workflow DevKit, AI Gateway… |
| `benchmark-e2e` | End-to-end benchmark suite for vercel-plugin. |
| `benchmark-sandbox` | Run vercel-plugin eval scenarios in Vercel Sandboxes instead of local WezTerm panels. |
| `benchmark-testing` | Create and launch benchmark test projects to exercise vercel-plugin skill injection across realistic scenarios. |
| `bootstrap` | Project bootstrapping orchestrator for repos that depend on Vercel-linked resources (databases, auth, and managed int… |
| `chat-sdk` | Vercel Chat SDK expert guidance. |
| `deployments-cicd` | Vercel deployment and CI/CD expert guidance. |
| `env-vars` | Vercel environment variable expert guidance. |
| `knowledge-update` | Corrects outdated LLM knowledge about the Vercel platform and introduces new products. |
| `marketplace` | Vercel Marketplace expert guidance — discovering, installing, and building integrations, auto-provisioned environment… |
| `next-cache-components` | Next.js 16 Cache Components guidance — PPR, use cache directive, cacheLife, cacheTag, updateTag, and migration from u… |
| `next-forge` | next-forge expert guidance — production-grade Turborepo monorepo SaaS starter by Vercel. |
| `next-upgrade` | Upgrade Next.js to the latest version following official migration guides and codemods. |
| `nextjs` | Next.js App Router expert guidance. |
| `plugin-audit` | Audit vercel-plugin performance on real-world projects. |
| `react-best-practices` | React best-practices reviewer for TSX files. |
| `release` | Release vercel-plugin — run gates, bump version, generate artifacts, commit, and push. |
| `routing-middleware` | Vercel Routing Middleware guidance — request interception before cache, rewrites, redirects, personalization. |
| `runtime-cache` | Vercel Runtime Cache API guidance — ephemeral per-region key-value cache with tag-based invalidation. |
| `shadcn` | shadcn/ui expert guidance — CLI, component installation, composition patterns, custom registries, theming, Tailwind C… |
| `turbopack` | Turbopack expert guidance. |
| `upstream` | Deploy, manage, and develop projects on Vercel from the command line |
| `vercel-agent` | Vercel Agent guidance — AI-powered code review, incident investigation, and SDK installation. |
| `vercel-cli` | Vercel CLI expert guidance. |
| `vercel-functions` | Vercel Functions expert guidance — Serverless Functions, Edge Functions, Fluid Compute, streaming, Cron Jobs, and run… |
| `vercel-plugin-eval` | Run live eval sessions against the vercel-plugin to verify hook behavior, skill injection, dedup correctness, and cov… |
| `vercel-sandbox` | Vercel Sandbox guidance — ephemeral Firecracker microVMs for running untrusted code safely. |
| `vercel-storage` | Vercel storage expert guidance — Blob, Edge Config, and Marketplace storage (Neon Postgres, Upstash Redis). |
| `verification` | Full-story verification — infers what the user is building, then verifies the complete flow end-to-end: browser → API… |
| `workflow` | Vercel Workflow DevKit (WDK) expert guidance. |

</details>

<details><summary><b>watch@claude-video</b> — 1 skills · Claude Code plugin</summary>

| Skill | What it does |
|---|---|
| `watch` | Watch a video (URL or local path). |

</details>

## License

Routing docs, templates and the `codex` skill: MIT © 2026 Aidan Pierce.
Every skill in `skills/` keeps its original author's license (MIT or Apache-2.0, included in its folder); sources are credited in the catalog above.
