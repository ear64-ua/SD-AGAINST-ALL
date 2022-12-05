read -p 'Engine nº: ' n_engine

base="api_engine"
base_engine="src-aa_engine-$n_engine"


# get each field
engine=$(docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)| grep $base_engine)

# substract ip from string
ip_engine=$(echo $engine| cut -d' ' -f 3)

echo "Engine: $ip_engine"

docker exec -it $base node api_engine.js $ip_engine




