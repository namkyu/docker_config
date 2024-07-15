
docker-compose up -d
TIMEOUT /t 5
docker-compose.exe exec mariadb sh ./test_db/init_db.sh