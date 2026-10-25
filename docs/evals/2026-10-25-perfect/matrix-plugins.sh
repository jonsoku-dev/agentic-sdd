#!/bin/sh
# usage: matrix-plugins.sh <sl> <outdir> <tag-digit>  — the plugin matrix from definition.md
SL=$1; O=$2; k=$3; R=$(dirname "$0")/../2026-10-24-single-loop-ab/run3.sh
mkdir -p $O
for ed in pfree pguard; do
  for n in 1 2 3 4 5 6; do sh $R $SL claude base $ed S so$k$n $O sonnet & sh $R $SL claude base2 $ed K so$k$n $O sonnet & done
  for n in 1 2; do sh $R $SL claude base2 $ed K op$k$n $O opus & done
  for n in 1 2 3 4 5 6; do sh $R $SL claude base $ed L op$k$n $O opus & done
done
(sh $R $SL codex base pfree S cx${k}1 $O; sh $R $SL codex base pfree S cx${k}2 $O) &
(sh $R $SL codex base2 pfree K cx${k}1 $O; sh $R $SL codex base2 pfree K cx${k}2 $O) &
wait
