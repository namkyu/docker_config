#!/bin/bash

echo ${MYSQL_ROOT_PASSWORD}

cd test_db
mariadb -u root -p${MYSQL_ROOT_PASSWORD} < create_database.sql