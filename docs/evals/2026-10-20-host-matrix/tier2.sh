#!/bin/sh
# usage: tier2.sh <host> <outdir>
host=$1; out=$2; S=<scratchpad>
prompt="Final Goal: add a 'todo edit <id> <new text>' subcommand to this repository's todo CLI (replaces the item's text; unknown id exits non-zero with a stderr message; tests cover both) as a new numbered Spec Kit feature, delivered end to end through the agentic-sdd skill in Economy cost mode: specify, plan, tasks, implement, converge (once only), then REA closeout. Fully autonomous, no questions, commit as you go. Record every breadcrumb in progress.md. Stop when progress.md states the Final Goal is met."
cd "$S/hm/$host" || exit 1
start=$(date +%s)
case $host in
  claude) claude -p --output-format stream-json --verbose --dangerously-skip-permissions --max-turns 150 "$prompt" > "$out/$host.jsonl" 2> "$out/$host.err" ;;
  codex)  codex exec --json --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m gpt-6-luna "$prompt" < /dev/null > "$out/$host.jsonl" 2> "$out/$host.err" ;;
  cursor) agent -p --output-format stream-json --force "$prompt" > "$out/$host.jsonl" 2> "$out/$host.err" ;;
  grok)   grok --output-format json --always-approve -p "$prompt" < /dev/null > "$out/$host.jsonl" 2> "$out/$host.err" ;;
esac
echo "$host rc=$? $(( $(date +%s) - start ))s" >> "$out/runs.log"
