
docker-compose.exe up -d
TIMEOUT /t 5
docker-compose.exe exec mariadb sh init_db.sh