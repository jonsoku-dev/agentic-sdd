#!/bin/sh
# usage: matrix.sh <sl> <version> <outdir>  — the 14-run matrix from definition.md
SL=$1; v=$2; O=$3; R=$(dirname "$0")/../2026-10-24-single-loop-ab/run3.sh
mkdir -p $O
for n in 1 2; do
  sh $R $SL claude base $v S so$n $O sonnet & sh $R $SL claude base $v L so$n $O sonnet &
  sh $R $SL claude base $v L op$n $O opus & sh $R $SL claude base $v L op$((n+2)) $O opus &
done
for n in 1 2 3 4 5 6; do sh $R $SL grok base $v S gk$n $O & done
(sh $R $SL codex base $v S cx1 $O; sh $R $SL codex base $v S cx2 $O) &
(sh $R $SL codex base $v L cx1 $O; sh $R $SL codex base $v L cx2 $O) &
wait
