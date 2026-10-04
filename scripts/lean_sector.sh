#!/bin/zsh
# Lean launch of ONE sector: (1) Python builds + writes the sector matrix and EXITS; (2) ktsolve runs ALONE on the
# file (nothing else resident); (3) Python finishes: residual guard against the file, reducible span, hashes, json,
# and deletes the matrix files. Usage: lean_sector.sh <metric> <rank> <denpow> <prime> <sector> <outdir> [templates-cache]
cd "${0:A:h}/.." || exit 2
M=$1; R=$2; D=$3; P=$4; S=$5; O=$6; C=${7:-}
CA=(); [ -n "$C" ] && CA=(--templates-cache $C)
common=(--metric $M --rank $R --denpow $D --prime $P --sectors $S --outdir $O $CA)
KT_SOLVER=rust .venv/bin/python -u scripts/_kt_exact_sector.py $common --phase write || exit 11
K=$(ls $O/*_r${R}_d${D}_*_p${P}_s${S}.ktm 2>/dev/null | head -1); [ -n "$K" ] || { echo "no matrix file written"; exit 12; }
echo "  [lean] ktsolve alone on $K ($(du -h $K | cut -f1)) -- $(date '+%H:%M:%S')"
rust/ktsolve/target/release/ktsolve --input $K --output $K.kts --threads ${KT_THREADS:-1} > $K.stats || exit 13
echo "  [lean] ktsolve done -- $(date '+%H:%M:%S')"
KT_SOLVER=rust .venv/bin/python -u scripts/_kt_exact_sector.py $common --phase finish || exit 14
