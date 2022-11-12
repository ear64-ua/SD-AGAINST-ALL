
read -p 'Player nº: ' n_player
read -p 'Engine nº: ' n_engine

base_player="src-aa_player-$n_player"
base_engine="src-aa_engine-$n_engine"
base_registry="aa_registry"

# get each field
engine=$(docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)| grep $base_engine)
registry=$(docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)| grep $base_registry)

# substract ip from string
ip_engine=$(echo $engine| cut -d' ' -f 3)
ip_registry=$(echo $registry| cut -d' ' -f 3)

echo "Engine: $ip_engine"
echo "Registry: $ip_registry"

docker exec -it $base_player python3 AA_Player.py $ip_engine $ip_registry




