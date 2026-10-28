#!/bin/bash
# usage: bake_pv.sh <gun> [H]   -> preview bake into $PV/<gun>pv, log /tmp/bake_pv_<gun>.log
G=$1; HH=${2:-0.20}
cd /home/claude/bolt-rifle-test/bolt-rifle-neoforge/tools
H=$HH python3 gen_guns.py /tmp/claude-0/-home-claude/f7704eef-62d6-5370-832a-86ddeef93d7b/scratchpad/${G}pv $G > /tmp/bake_pv_$G.log 2>&1
echo done >> /tmp/bake_pv_$G.log
