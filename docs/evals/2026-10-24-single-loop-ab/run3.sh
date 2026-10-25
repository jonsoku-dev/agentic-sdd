#!/bin/sh
# usage: run3.sh <sl-root> <host claude|codex|grok> <base dir name> <version> <brief S|L|K> <rep> <outdir> [model]
# One isolated headless run. Claude: --setting-sources project + --plugin-dir pstack + strict MCP.
# Codex: HOME and CODEX_HOME point at throwaway dirs holding only auth, pstack, the pstack AGENTS.md block, and REA.
# Grok: HOME and GROK_HOME are throwaway dirs holding only auth (keychain linked); no pstack, no REA MCP.
SL=$1; host=$2; base=$3; v=$4; brief=$5; rep=$6; out=$7; model=$8
tag="$host-$base-$v-$brief-$rep"; dir="$SL/runs/$tag"
rm -rf "$dir"; mkdir -p "$SL/runs" "$out"; cp -R "$SL/$base" "$dir"
# v = pfree / pguard: load the plugin edition from $SL/market instead of a project skill copy
case $v in pfree) plugin="$SL/market/plugins/agentic-sdd" ;; pguard) plugin="$SL/market/plugins/agentic-sdd-guarded" ;; *) plugin="" ;; esac
case $host in
  claude) [ -z "$plugin" ] && mkdir -p "$dir/.claude/skills" && cp -R "$SL/skill/$v" "$dir/.claude/skills/agentic-sdd" ;;
  codex)  (cd "$dir" && specify init --here --force --non-interactive --integration codex --integration-options="--skills" < /dev/null > /dev/null 2>&1)
          [ -z "$plugin" ] && mkdir -p "$dir/.agents/skills" && cp -R "$SL/skill/$v" "$dir/.agents/skills/agentic-sdd" ;;
  grok)   mkdir -p "$dir/.grok/skills" && cp -R "$dir"/.claude/skills/* "$dir/.grok/skills/" && cp -R "$SL/skill/$v" "$dir/.grok/skills/agentic-sdd" ;;
esac
(cd "$dir" && git add -A && git commit -qm "install agentic-sdd $v for $host" --allow-empty)
case $brief in
  S) goal="add a 'todo edit <id> <new text>' subcommand to this repository's todo CLI (replaces the item's text; unknown id exits non-zero with a stderr message; tests cover both)" ;;
  L) goal="extend this todo CLI with (1) priorities 1-3 via 'todo add --priority N' shown in list, (2) due dates via 'todo add --due YYYY-MM-DD', (3) 'todo list --sort due|priority' and 'todo list --overdue', (4) migration of existing stores written by the current version with no data loss, (5) tests for every new behaviour. Keep specs small: if the task list exceeds about 12 tasks, split into several numbered specs and finish them in order" ;;
  K) goal="add key expiry to this kv CLI: 'kv set <key> <value> --ttl <seconds>' makes the key expire after that many seconds; an expired key is absent from 'kv get' (exit 1 with a stderr message) and from 'kv list'; 'kv ttl <key>' prints the remaining whole seconds, and exits 1 with a stderr message when the key is missing or has no TTL; stores written by the current version keep working; node tests cover each behaviour" ;;
esac
prompt="Final Goal: $goal. Deliver it as new numbered Spec Kit features end to end through the agentic-sdd skill: specify, plan, tasks, implement, converge (once per spec), then REA closeout. Fully autonomous, no questions, commit as you go. Record every breadcrumb in progress.md. Stop when progress.md states the Final Goal is met."
cd "$dir" || exit 1
start=$(date +%s)
case $host in
  claude) claude -p --model "${model:-opus}" --output-format stream-json --verbose --dangerously-skip-permissions \
            --setting-sources project --strict-mcp-config --mcp-config "$SL/rea-mcp.json" \
            --plugin-dir "$SL/pstack" ${plugin:+--plugin-dir "$plugin"} --max-turns 250 --max-budget-usd 30 \
            "$prompt" < /dev/null > "$out/$tag.jsonl" 2> "$out/$tag.err" ;;
  codex)  fh="$SL/fakehome-$tag"; rm -rf "$fh"; mkdir -p "$fh"
          HOME="$fh" CODEX_HOME="$SL/codex-home${plugin:+-pfree}" GIT_AUTHOR_NAME=eval GIT_AUTHOR_EMAIL=eval@example.invalid \
            GIT_COMMITTER_NAME=eval GIT_COMMITTER_EMAIL=eval@example.invalid \
            codex exec --json --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox ${model:+-m "$model"} \
            "$prompt" < /dev/null > "$out/$tag.jsonl" 2> "$out/$tag.err" ;;
  grok)   fh="$SL/fakehome-$tag"; rm -rf "$fh"; mkdir -p "$fh/.grok" "$fh/Library"; ln -s "$HOME/Library/Keychains" "$fh/Library/Keychains"
          cp "$HOME/.grok/auth.json" "$fh/.grok/"
          HOME="$fh" GROK_HOME="$fh/.grok" GIT_AUTHOR_NAME=eval GIT_AUTHOR_EMAIL=eval@example.invalid \
            GIT_COMMITTER_NAME=eval GIT_COMMITTER_EMAIL=eval@example.invalid \
            grok --output-format json --always-approve -p "$prompt" < /dev/null > "$out/$tag.jsonl" 2> "$out/$tag.err" ;;
esac
echo "$tag rc=$? $(( $(date +%s) - start ))s" >> "$out/runs.log"
