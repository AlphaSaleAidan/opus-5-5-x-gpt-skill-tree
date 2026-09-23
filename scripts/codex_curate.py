"""Curate which skills Codex (GPT builders) loads: its skill list has a fixed text budget, so fewer
skills = longer descriptions = better triggering. Disabled skills stay available to Claude."""
import json, os, re, subprocess

HOME = os.path.expanduser('~')
ROOTS = {'r0': f'{HOME}/.codex/skills', 'r1': f'{HOME}/.agents/skills', 'r2': f'{HOME}/.codex/skills/.system'}

# 1) Claude Code plugin skills load only in Claude — link the builder-relevant ones into ~/.agents/skills for Codex.
KEEP_PLUGINS = ('hyperframes@', 'vercel@', 'stripe@')
PLUGIN_INTERNAL = {'upstream', 'plugin-audit', 'benchmark-testing', 'benchmark-agents', 'benchmark-sandbox',
                   'benchmark-e2e', 'vercel-plugin-eval', 'release', 'knowledge-update', 'marketplace', 'bootstrap'}
try:
    plugins = json.load(open(f'{HOME}/.claude/plugins/installed_plugins.json'))['plugins']
except OSError:
    plugins = {}
for key, val in plugins.items():
    if not key.startswith(KEEP_PLUGINS):
        continue
    path = (val[0] if isinstance(val, list) else val)['installPath']
    for root, _, files in os.walk(path):
        name = os.path.basename(root)
        dst = f"{ROOTS['r1']}/{name}"
        if 'SKILL.md' in files and 'node_modules' not in root and name not in PLUGIN_INTERNAL and not os.path.exists(dst):
            os.symlink(os.path.realpath(root), dst)

# 2) Turn off skills builders don't need.
MARK = '# --- codex skill curation (managed; regenerate with codex_curate.py) ---'

# Direction / strategy / ops work that stays on Claude (Opus leads) — builders don't need it.
OFF = set('''ab-testing ad-creative ads analytics attribution churn-prevention cold-email competitor-profiling
content-strategy cro customer-research emails launch lead-magnets marketing-council marketing-ideas
marketing-loops marketing-plan marketing-psychology offers onboarding paywalls popups pricing product-marketing
prospecting referrals revops sales-enablement signup sms social doc-coauthoring grilling research
seo seo-ahrefs seo-backlinks seo-bing seo-cluster seo-competitor-pages seo-content seo-content-brief
seo-dataforseo seo-drift seo-ecommerce seo-firecrawl seo-flow seo-geo seo-google seo-local seo-maps seo-plan
seo-profound seo-programmatic seo-seranking seo-sxo seo-unlighthouse seo-image-gen
create-assistant create-campaign setup-api-key simulations vapi-bootstrap-framework
n8n-agents-official n8n-binary-and-data-official n8n-code-nodes-official n8n-credentials-and-security-official
n8n-data-tables-official n8n-debugging-official n8n-error-handling-official n8n-expressions-official
n8n-extending-mcp-official n8n-loops-official n8n-node-configuration-official n8n-subworkflows-official
n8n-workflow-lifecycle-official using-n8n-skills-official
claude-settings-audit git-guardrails-claude-code writing-skills skill-writer plugin-creator
higgsfield-soul-id higgsfield-marketplace-cards

'''.split())
OFF_PREFIX = ('vapi-voice-ai:', 'shippo:', 'watch:', 'claude-flow:higgsfield-soul-id', 'claude-flow:higgsfield-marketplace-cards')
OFF_NS = {'ponytail:ponytail-audit', 'ponytail:ponytail-debt', 'ponytail:ponytail-gain', 'ponytail:ponytail-help',
          'stripe:stripe-projects', 'stripe:upgrade-stripe',
          'taste-skill:design-taste-frontend-v1', 'taste-skill:full-output-enforcement', 'taste-skill:stitch-design-taste',
          'taste-skill:brandkit',
          'hyperframes:captions-overlay', 'hyperframes:changelog-video', 'hyperframes:cut-the-curve', 'hyperframes:figma',
          'hyperframes:hyperframes-registry', 'hyperframes:motion-doctrine', 'hyperframes:music-to-video',
          'hyperframes:oversized-cursor', 'hyperframes:pr-to-video', 'hyperframes:remotion-to-hyperframes',
          'hyperframes:seam-craft', 'hyperframes:talking-head-recut', 'hyperframes:hyperframes-audio',
          'vercel:vercel-agent', 'vercel:next-forge', 'vercel:chat-sdk', 'vercel:vercel-sandbox', 'vercel:auth',
          'vercel:runtime-cache', 'vercel:routing-middleware', 'vercel:verification', 'vercel:workflow',
          'vercel:react-best-practices', 'vercel:vercel-react-best-practices', 'vercel:turbopack',
          'remotion-maps', 'remotion-saas', 'remotion-interactivity', 'remotion-upgrade', 'manim-video',
          'gsap-utils', 'gsap-frameworks', 'impeccable:impeccable'}

cfg_path = f'{HOME}/.codex/config.toml'
cfg = open(cfg_path).read() if os.path.exists(cfg_path) else ''
cfg = cfg.split('\n' + MARK)[0].rstrip() + '\n'
open(cfg_path, 'w').write(cfg)
s = subprocess.run(['codex', 'debug', 'prompt-input'], stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=HOME).stdout
entries = re.findall(r'\\n- ([a-z0-9:_-]+): .*? \(file: (r\d)/([^)]+)\)', s)
seen, off = set(), []
for name, root, rel in entries:
    path = f'{ROOTS[root]}/{rel}'
    base = name.split(':')[-1]
    dup = name in seen
    seen.add(name)
    if dup or base in OFF or name in OFF or name in OFF_NS or name.startswith(OFF_PREFIX):
        off.append(path)
block = [MARK] + [f'[[skills.config]]\npath = "{p}"\nenabled = false' for p in sorted(set(off))]
open(cfg_path, 'w').write(cfg + '\n' + '\n'.join(block) + '\n')
print(f'{len(entries)} listed, {len(set(off))} disabled for Codex, {len(entries) - len(set(off))} active')
