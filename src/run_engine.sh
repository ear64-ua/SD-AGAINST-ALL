
read -p 'Engine nº: ' n_engine
read -p 'Number of players nº: ' num_players
read -p 'Match time: ' match_time

base_engine="src-aa_engine-$n_engine"

# get each field
engine=$(docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)| grep $base_engine)

# substract ip from string
ip_engine=$(echo $engine| cut -d' ' -f 3)

echo "Engine: $ip_engine"

docker exec -it $base_engine python3 AA_Engine.py $ip_engine $num_players $match_time




