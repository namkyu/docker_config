# Run all containers
docker-compose up -d
sleep 10
# Execute Run init_rabbit.sh
docker-compose exec rabbit1 sh /init_rabbit.sh
sleep 5
# Restart Janus Server
docker-compose restart janus-container-01