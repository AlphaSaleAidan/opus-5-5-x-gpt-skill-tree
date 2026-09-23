#!/usr/bin/env bash
# Installs the full Opus 5.5 x GPT skill tree for Claude Code (~/.claude/skills) and Codex (~/.agents/skills).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ~/.claude/skills ~/.agents/skills
for d in skills/*/; do n=$(basename "$d"); rm -rf ~/.claude/skills/"$n" ~/.agents/skills/"$n"; cp -R "$d" ~/.claude/skills/"$n"; cp -R "$d" ~/.agents/skills/"$n"; done
echo "Copied 216 included skills."
# Skills whose licenses do not allow redistribution: pulled from the official repos.
npx -y skills add anthropics/skills -g -y -a claude-code codex -s frontend-design -s skill-creator -s webapp-testing
npx -y skills add openai/skills -g -y -a codex -s chatgpt-apps -s cli-creator -s define-goal -s gh-address-comments -s gh-fix-ci -s jupyter-notebook -s playwright -s playwright-interactive -s render-deploy -s screenshot -s security-best-practices -s security-ownership-map -s security-threat-model -s speech -s transcribe
npx -y skills add remotion-dev/skills -g -y -a claude-code codex -s remotion-best-practices -s remotion-captions -s remotion-create -s remotion-docs -s remotion-interactivity -s remotion-maps -s remotion-markup -s remotion-multimedia -s remotion-render -s remotion-saas -s remotion-studio -s remotion-upgrade
npx -y skills add vercel-labs/agent-skills -g -y -a claude-code codex -s deploy-to-vercel -s vercel-cli-with-tokens -s vercel-composition-patterns -s vercel-optimize -s vercel-react-best-practices -s vercel-react-native-skills -s vercel-react-view-transitions -s web-design-guidelines -s writing-guidelines
# Claude Code plugins (skip with NO_PLUGINS=1).
if [ -z "${NO_PLUGINS:-}" ] && command -v claude >/dev/null; then
  claude plugin marketplace add anthropics/claude-plugins-official || true
  claude plugin marketplace add bradautomates/claude-video || true
  claude plugin marketplace add VapiAI/skills || true
  claude plugin install claude-md-management@claude-plugins-official || true
  claude plugin install hookify@claude-plugins-official || true
  claude plugin install hyperframes@claude-plugins-official || true
  claude plugin install session-report@claude-plugins-official || true
  claude plugin install shippo@claude-plugins-official || true
  claude plugin install stripe@claude-plugins-official || true
  claude plugin install vapi-voice-ai@vapi-skills || true
  claude plugin install vercel@claude-plugins-official || true
  claude plugin install watch@claude-video || true
fi
# Codex: expose plugin skills to GPT, then curate the list (its skill-list text budget is fixed).
command -v codex >/dev/null && python3 scripts/codex_curate.py || true
echo "Done. Ponytail: enable it from claude.ai → Plugins. Restart Claude Code / Codex to load new skills."
