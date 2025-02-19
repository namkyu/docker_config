
docker-compose up -d
sleep 10

docker-compose exec rabbit sh init_rabbit.sh
sleep 5

docker-compose restart janus
sleep 5