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
  xrun|xrun-waves)
    root=$PWD
    work=$(mktemp -d)
    cd "$work"
    cp "$root/rtl/vigia.sv" "$root/sim/tb.sv" .
    options=()
    if [[ "$1" == xrun-waves ]]; then
        capture=$(mktemp -d "$root/build/xcelium-waves.XXXXXXXX")
        export T3_GUARD_SHM="$capture/t3-guard.shm"
        options=(-access +r -input "$root/sim/waves.tcl")
    fi
    xrun -64bit -sv -timescale 1ns/1ps -top tb "${options[@]}" vigia.sv tb.sv
    cp trace.csv exhaustive.csv xrun.log "$root/build/"
    if [[ "$1" == xrun-waves ]]; then
        test -d "$T3_GUARD_SHM"
        printf 'Abra no SimVision:\n  simvision -waves -input "%s" "%s"\n' "$root/sim/simvision.tcl" "$T3_GUARD_SHM"
    fi
    ;;
  *) echo "Uso: bash sim/run.sh [iverilog|xrun|xrun-waves]" >&2; exit 2 ;;
esac
