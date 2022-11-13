
read -p 'Number of engines: ' engines
read -p 'Number of weathers: ' weathers
read -p 'Number of players: ' players
read -p 'Number of NPCs: ' npcs

docker compose up --build -d --scale aa_player=$players --scale aa_engine=$engines --scale aa_npc=$npcs --scale aa_weather=$weathers

docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)