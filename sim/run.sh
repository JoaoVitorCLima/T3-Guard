#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
case "${1:-iverilog}" in
  iverilog)
    cd build
    iverilog -g2012 -s tb -o vigia_tb ../rtl/vigia.sv ../sim/tb.sv
    vvp vigia_tb
    ;;
  xrun)
    root=$PWD
    work=$(mktemp -d)
    cd "$work"
    cp "$root/rtl/vigia.sv" "$root/sim/tb.sv" .
    xrun -64bit -sv -timescale 1ns/1ps -top tb vigia.sv tb.sv
    cp trace.csv exhaustive.csv xrun.log "$root/build/"
    ;;
  *) echo "Uso: bash sim/run.sh [iverilog|xrun]" >&2; exit 2 ;;
esac
