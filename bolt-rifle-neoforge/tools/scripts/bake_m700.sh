cd /home/claude/bolt-rifle-test/bolt-rifle-neoforge/tools
python3 gen_guns.py ../src/main/resources m700 > /tmp/bake_m700.log 2>&1
python3 gen_m700_anim.py ../src/main/resources >> /tmp/bake_m700.log 2>&1
echo done >> /tmp/bake_m700.log
