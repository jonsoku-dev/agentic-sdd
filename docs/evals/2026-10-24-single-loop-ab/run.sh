#!/bin/sh
# usage: run.sh <sl-root> <version> <brief S|L, optional mode letter E|T|B> <rep> <outdir> [model]
# Copies the base repo, installs agentic-sdd <version> as a project skill, runs one isolated headless session.
SL=$1; v=$2; brief=$3; rep=$4; out=$5; model=${6:-opus}
tag="$v-$brief-$rep"; dir="$SL/runs/$tag"
rm -rf "$dir"; mkdir -p "$SL/runs" "$out"; cp -R "$SL/base" "$dir"
mkdir -p "$dir/.claude/skills" && cp -R "$SL/skill/$v" "$dir/.claude/skills/agentic-sdd"
(cd "$dir" && git add -A && git commit -qm "install agentic-sdd $v as project skill")
case $brief in
  S*) prompt="Final Goal: add a 'todo edit <id> <new text>' subcommand to this repository's todo CLI (replaces the item's text; unknown id exits non-zero with a stderr message; tests cover both) as a new numbered Spec Kit feature, delivered end to end through the agentic-sdd skill: specify, plan, tasks, implement, converge (once only), then REA closeout. Fully autonomous, no questions, commit as you go. Record every breadcrumb in progress.md. Stop when progress.md states the Final Goal is met." ;;
  L*) prompt="Final Goal: extend this todo CLI with (1) priorities 1-3 via 'todo add --priority N' shown in list, (2) due dates via 'todo add --due YYYY-MM-DD', (3) 'todo list --sort due|priority' and 'todo list --overdue', (4) migration of existing stores written by the current version with no data loss, (5) tests for every new behaviour. Deliver through the agentic-sdd skill: specify, plan, tasks, implement, converge once, REA closeout. Keep specs small: if the task list exceeds about 12 tasks, split into several numbered specs and finish them in order; if converge's single fix round leaves gaps, mark the spec closed-carryover and specify the next smaller spec instead of reconverging. Fully autonomous, no questions, commit as you go, record every breadcrumb in progress.md. Stop when progress.md states the Final Goal is met or names the next spec as carryover." ;;
esac
case $brief in
  ?E) prompt="$prompt Use Economy cost mode." ;;
  ?T) prompt="$prompt Use Thorough cost mode; treat this as high-risk work." ;;
esac
cd "$dir" || exit 1
start=$(date +%s)
claude -p --model "$model" --output-format stream-json --verbose --dangerously-skip-permissions \
  --setting-sources project --strict-mcp-config --mcp-config "$SL/rea-mcp.json" \
  --plugin-dir "$SL/pstack" --max-turns 250 --max-budget-usd 30 \
  "$prompt" < /dev/null > "$out/$tag.jsonl" 2> "$out/$tag.err"
echo "$tag rc=$? $(( $(date +%s) - start ))s" >> "$out/runs.log"
