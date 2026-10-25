cd /home/claude/bolt-rifle-test/bolt-rifle-neoforge/tools
H=0.30 python3 gen_guns.py /tmp/claude-0/-home-claude-bolt-rifle-test/f7704eef-62d6-5370-832a-86ddeef93d7b/scratchpad/m700pv m700 > /tmp/bake_m700pv.log 2>&1
python3 gen_m700_anim.py /tmp/claude-0/-home-claude-bolt-rifle-test/f7704eef-62d6-5370-832a-86ddeef93d7b/scratchpad/m700pv >> /tmp/bake_m700pv.log 2>&1
echo done >> /tmp/bake_m700pv.log
