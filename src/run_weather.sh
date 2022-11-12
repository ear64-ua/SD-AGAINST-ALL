
read -p 'Weather nº: ' n_weather

base_weather="src-aa_weather-$n_weather"

# get each field
weather=$(docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)| grep $base_weather)

# substract ip from string
ip_weather=$(echo $weather| cut -d' ' -f 3)

echo "Weather: $ip_weather"

docker exec -it $base_weather python3 AA_Weather.py $ip_weather




