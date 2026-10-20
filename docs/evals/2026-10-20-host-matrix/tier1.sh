#!/bin/sh
# usage: tier1.sh <host> <id> <outdir>
host=$1; id=$2; out=$3; S=<scratchpad>
case $id in
  T) prompt="Fix a typo in specs/001-todo-cli/quickstart.md ('recieve' to 'receive'). Plan only: write one line naming every skill, playbook, or workflow you would invoke for this task (or 'none'), then stop. Do not edit files." ;;
  F) prompt="Add a 'todo edit <id> <new text>' subcommand with tests to this repository. Plan only: list, in order, every skill, playbook, and Spec Kit phase you would invoke for this task, then stop. Do not edit files." ;;
  B) prompt="Users report that 'todo done 1' sometimes leaves item 1 visible in 'todo list'. Plan only: list, in order, every skill, playbook, and workflow stage you would invoke to handle this, then stop. Do not edit files." ;;
  D) prompt="Should this project's JSON store be replaced by SQLite? Plan only: list, in order, every skill or playbook you would invoke to answer that, then stop. Do not edit files." ;;
esac
cd "$S/hm/$host" || exit 1
start=$(date +%s)
case $host in
  claude) claude -p --output-format stream-json --verbose --dangerously-skip-permissions --max-turns 10 "$prompt" > "$out/$host-$id.jsonl" 2> "$out/$host-$id.err" ;;
  codex)  codex exec --json --skip-git-repo-check -s read-only -m gpt-6-luna "$prompt" < /dev/null > "$out/$host-$id.jsonl" 2> "$out/$host-$id.err" ;;
  cursor) agent -p --output-format stream-json --trust "$prompt" > "$out/$host-$id.jsonl" 2> "$out/$host-$id.err" ;;
  grok)   grok --output-format json -p "$prompt" < /dev/null > "$out/$host-$id.jsonl" 2> "$out/$host-$id.err" ;;
esac
echo "$host $id rc=$? $(( $(date +%s) - start ))s" >> "$out/runs.log"
