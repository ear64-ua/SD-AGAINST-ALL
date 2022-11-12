
read -p 'Number of engine`s: ' engines
read -p 'Number of player`s: ' players
read -p 'Number of npc`s: ' npcs

docker compose up --build -d --scale aa_player=$players --scale aa_engine=$engines --scale aa_npc=$npcs

docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)