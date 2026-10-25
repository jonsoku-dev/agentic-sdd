#!/bin/sh
# usage: matrix.sh <sl> <version> <outdir>  — the 14-run matrix from definition.md
SL=$1; v=$2; O=$3; R=/Users/jongseoklee/Documents/GitHub/agentic-sdd/.claude/worktrees/agent-design-guidebook-a798bc/docs/evals/2026-10-24-single-loop-ab/run3.sh
mkdir -p $O
for n in 1 2; do
  sh $R $SL claude base $v S so$n $O sonnet & sh $R $SL claude base2 $v K so$n $O sonnet &
  sh $R $SL claude base2 $v K op$n $O opus & sh $R $SL claude base $v L op$n $O opus &
done
for n in 1 2 3 4 5 6; do sh $R $SL grok base $v S gk$n $O & done
(sh $R $SL codex base $v S cx1 $O; sh $R $SL codex base $v S cx2 $O) &
(sh $R $SL codex base2 $v K cx1 $O; sh $R $SL codex base2 $v K cx2 $O) &
wait
