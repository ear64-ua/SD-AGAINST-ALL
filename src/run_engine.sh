
read -p 'Engine nº: ' n_engine
read -p 'Weather nº: ' n_weather

base_engine="src-aa_engine-$n_engine"
base_weather="src-aa_weather-$n_weather"

# get each field
engine=$(docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)| grep $base_engine)
weather=$(docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)| grep $base_weather)

# substract ip from string
ip_engine=$(echo $engine| cut -d' ' -f 3)
ip_weather=$(echo $weather| cut -d' ' -f 3)

echo "Engine: $ip_engine"
echo "Weather: $ip_weather"

docker exec -it $base_engine python3 AA_Engine.py $ip_engine $ip_weather




