#!/bin/sh
# usage: tier3.sh <host> <dir> <outdir> <tag>
host=$1; dir=$2; out=$3; tag=$4
prompt="Final Goal: extend this todo CLI with (1) priorities 1-3 via 'todo add --priority N' shown in list, (2) due dates via 'todo add --due YYYY-MM-DD', (3) 'todo list --sort due|priority' and 'todo list --overdue', (4) migration of existing stores written by the current version with no data loss, (5) tests for every new behaviour. Deliver through the agentic-sdd skill in Economy cost mode: specify, plan, tasks, implement, converge once, REA closeout. Keep specs small: if the task list exceeds about 12 tasks, split into several numbered specs and finish them in order; if converge's single fix round leaves gaps, mark the spec closed-carryover and specify the next smaller spec instead of reconverging. Fully autonomous, no questions, commit as you go, record every breadcrumb in progress.md. Stop when progress.md states the Final Goal is met or names the next spec as carryover."
cd "$dir" || exit 1
start=$(date +%s)
case $host in
  claude) claude -p --output-format stream-json --verbose --dangerously-skip-permissions --max-turns 250 "$prompt" > "$out/$tag.jsonl" 2> "$out/$tag.err" ;;
  codex)  codex exec --json --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -m gpt-6-luna "$prompt" < /dev/null > "$out/$tag.jsonl" 2> "$out/$tag.err" ;;
  cursor) agent -p --output-format stream-json --force "$prompt" > "$out/$tag.jsonl" 2> "$out/$tag.err" ;;
  grok)   grok --output-format json --always-approve -p "$prompt" < /dev/null > "$out/$tag.jsonl" 2> "$out/$tag.err" ;;
esac
echo "$tag rc=$? $(( $(date +%s) - start ))s" >> "$out/runs.log"
