#!/usr/bin/env bash
# Link this skill into every host's skill directory (idempotent), optionally
# install the Cursor continuation hooks and a project playbook.
#
# Usage:
#   ./install.sh                         # symlink into ~/.agents, ~/.claude, ~/.codex, ~/.cursor, ~/.grok
#   ./install.sh --project DIR           # also copy templates/playbooks/agentic-sdd.md into DIR/.agents/playbooks/
#   ./install.sh --apply-cursor-hooks    # also install hosts/cursor/hooks into ~/.cursor (dated backup of hooks.json)
#   ./install.sh --grok-agents           # expose pstack's poteto-agent/comment-sicko to Grok's spawn_subagent enum
#   ./install.sh --grok-mandate          # write the pstack poteto-mode mandate + Spec Kit handoffs as a Grok home rule (~/.grok/rules/pstack-mandate.md)
#   ./install.sh --codex-mandate         # write the pstack poteto-mode mandate into ~/.codex/AGENTS.md (Codex never runs untrusted plugin hooks)
#   ./install.sh --deps                  # install/update Spec Kit, pstack (Claude/Codex/Grok), rea-agents pins to latest, then relink (scripts/deps.py update --yes)
#   ./install.sh --check-deps            # report installed vs latest for every dependency and exit 1 when something is behind
#   ./install.sh --cursor-cli-skills     # link the Cursor pstack plugin's skills into ~/.cursor/skills for the Cursor Agent CLI
#   ./install.sh --uninstall             # remove everything this script created under $HOME (symlinks, Grok rule/agents, Codex mandate block, Cursor links/hooks)
#   ./install.sh --uninstall --project DIR       # also remove DIR/.agents/playbooks/agentic-sdd.md and DIR/.cursor/rules/agentic-sdd.mdc
#   ./install.sh --uninstall --purge-deps --yes  # also uninstall pstack (Claude/Codex/Grok) and the Spec Kit CLI; rea MCP entries and pstack sheets stay

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="agentic-sdd"
PROJECT=""
APPLY_CURSOR_HOOKS=0
GROK_AGENTS=0
GROK_MANDATE=0
CODEX_MANDATE=0
DEPS=0
CHECK_DEPS=0
PURGE_DEPS=0
YES=0
CURSOR_CLI_SKILLS=0
UNINSTALL=0

while [ $# -gt 0 ]; do
  case "$1" in
    --project) PROJECT="$2"; shift 2 ;;
    --apply-cursor-hooks) APPLY_CURSOR_HOOKS=1; shift ;;
    --grok-agents) GROK_AGENTS=1; shift ;;
    --grok-mandate) GROK_MANDATE=1; shift ;;
    --codex-mandate) CODEX_MANDATE=1; shift ;;
    --deps) DEPS=1; shift ;;
    --check-deps) CHECK_DEPS=1; shift ;;
    --cursor-cli-skills) CURSOR_CLI_SKILLS=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --purge-deps) PURGE_DEPS=1; shift ;;
    --yes) YES=1; shift ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ "$CHECK_DEPS" = 1 ]; then
  exec python3 "$SRC/scripts/deps.py" check
fi
if [ "$DEPS" = 1 ] && [ "$UNINSTALL" = 0 ]; then
  python3 "$SRC/scripts/deps.py" update --yes || echo "deps: some updates failed; see above" >&2
fi

link_into() {
  local dir="$1"
  local target="$dir/$NAME"
  mkdir -p "$dir"
  if [ "$UNINSTALL" = 1 ]; then
    if [ -L "$target" ]; then rm "$target"; echo "removed $target"; fi
    return 0
  fi
  if [ "$(cd "$dir" 2>/dev/null && pwd -P)/$NAME" = "$SRC" ]; then
    echo "canonical $target"
    return
  fi
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "skip $target: exists and is not a symlink" >&2
    return
  fi
  ln -sfn "$SRC" "$target"
  echo "linked $target -> $SRC"
}

for d in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" \
         "$HOME/.cursor/skills" "$HOME/.grok/skills"; do
  link_into "$d"
done

if [ "$UNINSTALL" = 1 ]; then
  for f in "$HOME/.grok/agents/poteto-agent.md" "$HOME/.grok/agents/comment-sicko.md" "$HOME/.grok/hooks/pstack-session-start.json" "$HOME/.grok/rules/pstack-mandate.md"; do
    [ -L "$f" ] || [ -f "$f" ] && rm -f "$f" && echo "removed $f"
  done
  if [ -f "$HOME/.codex/AGENTS.md" ] && /usr/bin/grep -q 'pstack-mandate:start' "$HOME/.codex/AGENTS.md"; then
    python3 - "$HOME/.codex/AGENTS.md" <<'EOF'
import pathlib, sys
p = pathlib.Path(sys.argv[1]); t = p.read_text()
s, e = "<!-- pstack-mandate:start -->", "<!-- pstack-mandate:end -->"
p.write_text(t[:t.index(s)].rstrip("\n") + "\n" + t[t.index(e) + len(e):].lstrip("\n"))
print("removed pstack mandate block from", p)
EOF
  fi
  for l in "$HOME"/.cursor/skills/*; do
    [ -L "$l" ] && case "$(readlink "$l")" in */cursor-public/pstack/*) rm "$l"; echo "removed $l";; esac
  done
  HOOK_DIR="$HOME/.cursor/hooks/$NAME-continue"
  if [ -d "$HOOK_DIR" ]; then rm -rf "$HOOK_DIR"; echo "removed $HOOK_DIR"; fi
  HOOKS="$HOME/.cursor/hooks.json"
  if [ -f "$HOOKS" ]; then
    python3 - "$HOOKS" <<'EOF'
import json, sys, pathlib
dst = pathlib.Path(sys.argv[1])
data = json.loads(dst.read_text())
hooks = data.get("hooks") or {}
changed = False
for event, entries in list(hooks.items()):
    kept = [h for h in entries if "agentic-sdd-continue" not in h.get("command", "")]
    if kept != entries:
        changed = True
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
if changed:
    dst.write_text(json.dumps(data, indent=2) + "\n")
    print(f"removed agentic-sdd Cursor hooks from {dst}")
EOF
  fi
  if [ -n "$PROJECT" ]; then
    for f in "$PROJECT/.agents/playbooks/$NAME.md" "$PROJECT/.cursor/rules/$NAME.mdc"; do
      if [ -f "$f" ]; then rm "$f"; echo "removed $f"; fi
    done
    rmdir "$PROJECT/.agents/playbooks" "$PROJECT/.agents" "$PROJECT/.cursor/rules" 2>/dev/null || true
  fi
  if [ "$PURGE_DEPS" = 1 ]; then
    if [ "$YES" != 1 ]; then
      echo "--purge-deps removes pstack from Claude Code, Codex, and Grok and the Spec Kit CLI; rerun with --yes to confirm" >&2
    else
      command -v claude >/dev/null && claude plugin uninstall pstack@pstack-claude 2>&1 | tail -1
      command -v codex >/dev/null && codex plugin remove pstack 2>&1 | tail -1
      if command -v grok >/dev/null; then
        for n in $(grok plugin list 2>/dev/null | awk -F: '/^  pstack-/{print $1}'); do grok plugin uninstall "$n" 2>&1 | tail -1; done
      fi
      command -v uv >/dev/null && uv tool uninstall specify-cli 2>&1 | tail -1
      echo "purged pstack plugins and the Spec Kit CLI; remove Cursor's pstack from the IDE (Settings > Plugins)"
    fi
  fi
  cat <<KEPT
kept on purpose (remove by hand if you want them gone):
  rea MCP entries in ~/.claude.json, ~/.cursor/mcp.json, ~/.codex/config.toml, ~/.grok/config.toml (this script only repins their version)
  pstack model sheets: ~/.claude/pstack-models.md, ~/.codex/pstack-models.md, ~/.cursor/rules/pstack-models.mdc, ~/.grok/pstack-models.md
  backups this script wrote: ~/.cursor/hooks.json.bak-*, <config>.bak-rea-<version>
  your projects' .specify/, specs/, progress.md
  this checkout: rm -rf "$SRC"
KEPT
  exit 0
fi

if [ -n "$PROJECT" ] && [ "$UNINSTALL" = 0 ]; then
  mkdir -p "$PROJECT/.agents/playbooks"
  cp "$SRC/templates/playbooks/$NAME.md" "$PROJECT/.agents/playbooks/$NAME.md"
  echo "installed project playbook $PROJECT/.agents/playbooks/$NAME.md (pstack-claude port only)"
  mkdir -p "$PROJECT/.cursor/rules"
  cp "$SRC/templates/cursor-rules/$NAME.mdc" "$PROJECT/.cursor/rules/$NAME.mdc"
  echo "installed Cursor rule $PROJECT/.cursor/rules/$NAME.mdc (Cursor plugin has no project playbooks)"
fi

if [ "$APPLY_CURSOR_HOOKS" = 1 ] && [ "$UNINSTALL" = 0 ]; then
  mkdir -p "$HOME/.cursor/hooks"
  rm -rf "$HOME/.cursor/hooks/$NAME-continue"
  cp -R "$SRC/hosts/cursor/hooks/$NAME-continue" "$HOME/.cursor/hooks/$NAME-continue"
  chmod +x "$HOME/.cursor/hooks/$NAME-continue/"*.sh
  HOOKS="$HOME/.cursor/hooks.json"
  if [ -f "$HOOKS" ]; then cp "$HOOKS" "$HOOKS.bak-$(date +%Y%m%d-%H%M%S)"; fi
  python3 - "$HOOKS" "$SRC/hosts/cursor/hooks.snippet.json" <<'EOF'
import json, sys, pathlib
dst, snip = pathlib.Path(sys.argv[1]), json.loads(pathlib.Path(sys.argv[2]).read_text())
data = json.loads(dst.read_text()) if dst.is_file() else {"version": 1, "hooks": {}}
hooks = data.setdefault("hooks", {})
for event, entries in snip["hooks"].items():
    cur = [h for h in hooks.get(event, []) if "agentic-sdd-continue" not in h.get("command", "")]
    hooks[event] = cur + entries if event != "stop" else cur + entries  # stop hook stays last
dst.write_text(json.dumps(data, indent=2) + "\n")
print(f"merged Cursor hooks into {dst}")
EOF
fi

if [ "$GROK_AGENTS" = 1 ] && [ "$UNINSTALL" = 0 ]; then
  # Grok loads pstack skills via the plugin but does not list its plugin agents in
  # spawn_subagent's enum; a user-level agent file does appear there.
  PSTACK_AGENTS=""
  for cand in "$HOME"/.grok/marketplace-cache/*/plugins/pstack/agents \
              "$HOME"/.claude/plugins/marketplaces/pstack-claude/plugins/pstack/agents \
              "$HOME"/.claude/plugins/cache/pstack-claude/pstack/*/agents; do
    [ -d "$cand" ] && PSTACK_AGENTS="$cand" && break
  done
  if [ -n "$PSTACK_AGENTS" ]; then
    mkdir -p "$HOME/.grok/agents"
    for a in poteto-agent comment-sicko; do
      ln -sfn "$PSTACK_AGENTS/$a.md" "$HOME/.grok/agents/$a.md" && echo "linked ~/.grok/agents/$a.md"
    done
  else
    echo "skip --grok-agents: no pstack agents directory found" >&2
  fi
fi

if [ "$CODEX_MANDATE" = 1 ] && [ "$UNINSTALL" = 0 ]; then
  # Codex runs the plugin's SessionStart hook only after /hooks trust and never under
  # `codex exec`, so the mandate lives in ~/.codex/AGENTS.md between markers.
  PSTACK_ROOT=""
  for cand in "$HOME"/.codex/plugins/cache/*/pstack/* \
              "$HOME"/.claude/plugins/marketplaces/pstack-claude/plugins/pstack \
              "$HOME"/.claude/plugins/cache/pstack-claude/pstack/*; do
    [ -f "$cand/hooks/session-start-context.md" ] && PSTACK_ROOT="$cand" && break
  done
  if [ -n "$PSTACK_ROOT" ]; then
    mkdir -p "$HOME/.codex"
    python3 - "$HOME/.codex/AGENTS.md" "$PSTACK_ROOT/hooks/session-start-context.md" <<'EOF'
import pathlib, sys
agents, ctx = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).read_text().strip()
s, e = "<!-- pstack-mandate:start -->", "<!-- pstack-mandate:end -->"
block = (f"{s}\n# pstack poteto-mode mandate (Codex)\n\nSame text the pstack SessionStart hook injects on Claude Code. "
         f"Kept here because Codex runs plugin hooks only after `/hooks` trust, and `codex exec` never trusts them.\n\n{ctx}\n{e}\n")
t = agents.read_text() if agents.is_file() else ""
t = t[:t.index(s)] + block + t[t.index(e) + len(e):].lstrip("\n") if s in t and e in t else t.rstrip("\n") + "\n\n" + block
agents.write_text(t)
print("wrote pstack mandate block into", agents)
EOF
  else
    echo "pstack plugin root not found; skipped --codex-mandate" >&2
  fi
fi

if [ "$GROK_MANDATE" = 1 ] && [ "$UNINSTALL" = 0 ]; then
  # Grok runs SessionStart hooks but treats their stdout as passive (never injected),
  # so the pstack mandate goes into a home-level rule, which Grok always loads.
  PSTACK_ROOT=""
  for cand in "$HOME"/.grok/marketplace-cache/*/plugins/pstack \
              "$HOME"/.claude/plugins/marketplaces/pstack-claude/plugins/pstack \
              "$HOME"/.claude/plugins/cache/pstack-claude/pstack/*; do
    [ -f "$cand/hooks/session-start-context.md" ] && PSTACK_ROOT="$cand" && break
  done
  if [ -n "$PSTACK_ROOT" ]; then
    mkdir -p "$HOME/.grok/rules"
    { printf '%s\n\n' "# pstack mandate (copied from the plugin SessionStart hook; Grok does not inject hook stdout)"
      cat "$PSTACK_ROOT/hooks/session-start-context.md"
      printf '\n%s\n\n' "On Grok Build, plugin agents are not in the spawn_subagent enum; use subagent_type \"poteto-agent\" (user agent linked by install.sh --grok-agents) or general-purpose with an instruction to read poteto-mode/SKILL.md first."
      # Spec Kit handoffs, same three as the project playbook / Cursor rule, so a bug or feature
      # in a Spec Kit repo resolves the phase before any poteto playbook runs.
      printf '%s\n\n' "# agentic-sdd handoffs (Spec Kit owns the phases)"
      awk '/^- Any feature, bug, or multi-file change/{p=1} /^- Read `poteto-mode\/SKILL.md`/{p=0} p' "$SRC/templates/cursor-rules/$NAME.mdc" \
        | sed "s/O-poteto|cursor|/O-poteto|grok|/"; } \
      > "$HOME/.grok/rules/pstack-mandate.md"
    rm -f "$HOME/.grok/hooks/pstack-session-start.json"
    echo "wrote ~/.grok/rules/pstack-mandate.md"
  else
    echo "skip --grok-mandate: pstack session-start-context.md not found" >&2
  fi
fi

if [ "$CURSOR_CLI_SKILLS" = 1 ] && [ "$UNINSTALL" = 0 ]; then
  # The Cursor IDE loads marketplace plugin skills; the Cursor Agent CLI reads
  # ~/.cursor/skills only. Link the official plugin's skills there.
  CURSOR_PSTACK=""
  for cand in "$HOME"/.cursor/plugins/cache/cursor-public/pstack/*/skills; do
    [ -d "$cand" ] && CURSOR_PSTACK="$cand"
  done
  if [ -n "$CURSOR_PSTACK" ]; then
    # The plugin cache path carries a content hash that changes on every plugin
    # update, so prune links into older pstack caches before relinking.
    for l in "$HOME"/.cursor/skills/*; do
      [ -L "$l" ] && case "$(readlink "$l")" in */cursor-public/pstack/*) [ -e "$l" ] || rm "$l";; esac
    done
    n=0
    for sk in "$CURSOR_PSTACK"/*/; do
      name="$(basename "$sk")"
      target="$HOME/.cursor/skills/$name"
      if [ -e "$target" ] && [ ! -L "$target" ]; then continue; fi
      ln -sfn "${sk%/}" "$target" && n=$((n+1))
    done
    echo "linked $n Cursor pstack skills into ~/.cursor/skills"
  else
    echo "skip --cursor-cli-skills: Cursor pstack plugin not found" >&2
  fi
fi

if [ "$UNINSTALL" = 0 ]; then
  cat <<'EOF'

pstack (execution engine inside Spec Kit phases) is installed per host, once:
  Claude Code : claude plugin install pstack --marketplace michael-denyer/pstack-claude --scope user
  Codex       : codex plugin marketplace add michael-denyer/pstack-claude && codex plugin add pstack@pstack-claude
  Cursor      : /add-plugin pstack
  Grok Build  : grok plugin marketplace add michael-denyer/pstack-claude && grok plugin install pstack@pstack-claude --trust
Check: python3 scripts/harness_probe.py --host <claude|codex|cursor|grok> --project <repo>
EOF
fi
