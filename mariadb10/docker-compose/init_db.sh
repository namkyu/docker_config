#!/bin/bash

cd test_db
echo ${MYSQL_ROOT_PASSWORD}

mysql -u root -p${MYSQL_ROOT_PASSWORD} < employees.sql
mysql -u root -p${MYSQL_ROOT_PASSWORD} < room.sql