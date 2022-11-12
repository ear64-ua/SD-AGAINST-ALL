
read -p 'NPC nº: ' n_npc

base_npc="src-aa_npc-$n_npc"

docker exec -it $base_npc python3 AA_NPC.py




